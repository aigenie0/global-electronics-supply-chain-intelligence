# Platform Architecture

## Purpose

This platform analyzes public semiconductor trade data to identify supply concentration, manufacturing dependencies, disruption exposure, and realistic sourcing alternatives for the consumer-electronics industry.

## Planned Data Flow

UN Comtrade and other official public sources

↓

Snowflake raw data layer

↓

Data cleaning and standardization

↓

Analytics data layer

↓

Supply-chain metrics and scenario analysis

↓

Executive Power BI dashboard

## Snowflake Architecture

Snowflake separates the platform into three primary layers:

### Storage

Stores semiconductor trade records, country information, product classifications, and economic indicators.

### Compute

Uses virtual warehouses to run SQL queries, transformations, concentration calculations, and dashboard workloads.

### Cloud Services

Manages authentication, permissions, metadata, query optimization, and coordination between storage and compute.

## Planned Snowflake Structure

```text
SEMICONDUCTOR_SUPPLY_CHAIN_DB
│
├── RAW
│   └── Source data close to its original form
│
├── STAGING
│   └── Cleaned and standardized data
│
└── ANALYTICS
    └── Business-ready tables and calculated metrics
