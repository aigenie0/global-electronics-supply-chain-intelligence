from pathlib import Path
from datetime import datetime, timezone
import time

import comtradeapicall
import pandas as pd


# Extraction settings

REPORTER_CODE = "842"       # United States
FLOW_CODE = "M"             # Imports

YEARS = [
    2023,
    2024,
]

MONTHS = range(1, 13)

PRODUCTS = {
    "854231": "Processors and controllers",
    "854232": "Memory integrated circuits",
}


# Save files relative to the folder where Jupyter is running

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = (
    OUTPUT_DIRECTORY
    / "us_semiconductor_imports_monthly_2023_2024_preview.csv"
)

REQUEST_LOG_FILE = (
    OUTPUT_DIRECTORY
    / "us_semiconductor_imports_monthly_2023_2024_request_log.csv"
)


# Store successful responses and request results

extracted_datasets = []
request_log = []


# Run one request per month and product

for year in YEARS:
    for month in MONTHS:
        period = f"{year}{month:02d}"

        for hs_code, product_group in PRODUCTS.items():

            print(
                f"Requesting {period} — "
                f"{hs_code} — {product_group}"
            )

            trade_data = None
            error_message = None

            # Retry a failed request up to three times

            for attempt in range(1, 4):
                try:
                    trade_data = comtradeapicall.previewFinalData(
                        typeCode="C",
                        freqCode="M",
                        clCode="HS",
                        period=period,
                        reporterCode=REPORTER_CODE,
                        cmdCode=hs_code,
                        flowCode=FLOW_CODE,
                        partnerCode=None,
                        partner2Code=None,
                        customsCode=None,
                        motCode=None,
                        maxRecords=500,
                        format_output="JSON",
                        aggregateBy=None,
                        breakdownMode="classic",
                        countOnly=None,
                        includeDesc=True,
                    )

                    if (
                        isinstance(trade_data, pd.DataFrame)
                        and not trade_data.empty
                    ):
                        break

                    error_message = "API returned no records."

                except Exception as error:
                    error_message = str(error)

                print(
                    f"Attempt {attempt} failed: "
                    f"{error_message}"
                )

                if attempt < 3:
                    time.sleep(attempt * 2)


            # Log empty or failed requests

            if (
                trade_data is None
                or not isinstance(trade_data, pd.DataFrame)
                or trade_data.empty
            ):
                request_log.append(
                    {
                        "period": period,
                        "year": year,
                        "month": month,
                        "hs_code": hs_code,
                        "product_group": product_group,
                        "status": "FAILED_OR_EMPTY",
                        "rows_returned": 0,
                        "error": error_message,
                    }
                )

                print("No records saved.\n")
                continue


            # Add extraction metadata

            trade_data = trade_data.copy()

            trade_data["requestedYear"] = year
            trade_data["requestedMonth"] = month
            trade_data["requestedPeriod"] = period
            trade_data["requestedHSCode"] = hs_code
            trade_data["productGroup"] = product_group
            trade_data["extractionMethod"] = "previewFinalData"
            trade_data["extractedAtUTC"] = datetime.now(
                timezone.utc
            ).isoformat()


            # Store the successful result

            extracted_datasets.append(trade_data)

            request_log.append(
                {
                    "period": period,
                    "year": year,
                    "month": month,
                    "hs_code": hs_code,
                    "product_group": product_group,
                    "status": "SUCCESS",
                    "rows_returned": len(trade_data),
                    "error": None,
                }
            )

            print(f"Rows returned: {len(trade_data):,}\n")

            # Pause briefly between public API requests

            time.sleep(1)


# Create the request-log DataFrame

request_log_df = pd.DataFrame(request_log)

request_log_df.to_csv(
    REQUEST_LOG_FILE,
    index=False,
)


# Stop when no request returned usable data

if not extracted_datasets:
    raise RuntimeError(
        "No usable datasets were returned by UN Comtrade. "
        "Review the request log for details."
    )


# Combine all successful monthly responses

combined_data = pd.concat(
    extracted_datasets,
    ignore_index=True,
    sort=False,
)


# Store important identifiers as text

text_columns = [
    "period",
    "reporterCode",
    "reporterISO",
    "flowCode",
    "partnerCode",
    "partnerISO",
    "partner2Code",
    "partner2ISO",
    "classificationCode",
    "cmdCode",
    "requestedPeriod",
    "requestedHSCode",
]

for column in text_columns:
    if column in combined_data.columns:
        combined_data[column] = (
            combined_data[column]
            .astype("string")
            .str.strip()
        )


# Sort the combined extract

sort_columns = [
    column
    for column in [
        "requestedPeriod",
        "requestedHSCode",
        "partnerDesc",
    ]
    if column in combined_data.columns
]

combined_data = (
    combined_data
    .sort_values(sort_columns)
    .reset_index(drop=True)
)


# Save the combined raw extract

combined_data.to_csv(
    OUTPUT_FILE,
    index=False,
)


# Extraction summary

successful_requests = (
    request_log_df["status"]
    .eq("SUCCESS")
    .sum()
)

failed_requests = (
    request_log_df["status"]
    .ne("SUCCESS")
    .sum()
)

print("\nExtraction completed.")
print(f"Successful requests: {successful_requests}")
print(f"Failed or empty requests: {failed_requests}")
print(f"Total rows: {len(combined_data):,}")
print(f"Total columns: {len(combined_data.columns):,}")
print(f"Data file: {OUTPUT_FILE}")
print(f"Request log: {REQUEST_LOG_FILE}")


# Display request status

print("\nRequest log:")

display(request_log_df)


# Validate period coverage

period_summary = (
    combined_data
    .groupby(
        [
            "requestedYear",
            "requestedHSCode",
            "productGroup",
        ],
        dropna=False,
    )
    .agg(
        first_period=("requestedPeriod", "min"),
        last_period=("requestedPeriod", "max"),
        distinct_periods=("requestedPeriod", "nunique"),
        total_rows=("requestedPeriod", "size"),
        distinct_partners=("partnerDesc", "nunique"),
    )
    .reset_index()
)

period_summary["complete_12_months"] = (
    period_summary["distinct_periods"] == 12
)

print("\nPeriod coverage:")

display(period_summary)


# Check whether any expected requests are missing

expected_requests = (
    len(YEARS)
    * len(list(MONTHS))
    * len(PRODUCTS)
)

print("\nRequest completeness:")
print(f"Expected requests: {expected_requests}")
print(f"Successful requests: {successful_requests}")


# Check for duplicate records at the intended trade grain

grain_columns = [
    "period",
    "reporterCode",
    "partnerCode",
    "flowCode",
    "cmdCode",
]

duplicate_mask = combined_data.duplicated(
    subset=grain_columns,
    keep=False,
)

duplicate_row_count = int(duplicate_mask.sum())

print("\nDuplicate validation:")
print(
    "Rows involved in duplicate grain combinations:",
    duplicate_row_count,
)


# Display duplicate records only when found

if duplicate_row_count > 0:
    duplicate_records = (
        combined_data.loc[
            duplicate_mask,
            grain_columns
            + [
                "partnerDesc",
                "primaryValue",
                "isAggregate",
            ],
        ]
        .sort_values(grain_columns)
    )

    display(duplicate_records.head(50))


# Display World totals by year and product

world_totals = (
    combined_data.loc[
        combined_data["isAggregate"].eq(True)
        & combined_data["partnerDesc"].eq("World")
    ]
    .groupby(
        [
            "requestedYear",
            "requestedHSCode",
            "productGroup",
        ],
        dropna=False,
    )
    .agg(
        annual_world_import_value_usd=(
            "primaryValue",
            "sum",
        ),
        months_available=(
            "requestedPeriod",
            "nunique",
        ),
    )
    .reset_index()
)

print("\nReported World totals:")

display(world_totals)


# Inspect selected records

preview_columns = [
    "period",
    "reporterDesc",
    "partnerDesc",
    "flowDesc",
    "cmdCode",
    "productGroup",
    "primaryValue",
    "isReported",
    "isAggregate",
]

available_preview_columns = [
    column
    for column in preview_columns
    if column in combined_data.columns
]

print("\nFirst 20 records:")

display(
    combined_data[
        available_preview_columns
    ].head(20)
)
