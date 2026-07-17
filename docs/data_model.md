# Semiconductor Trade Data Model

## Grain

Each row in `FACT_SEMICONDUCTOR_TRADE` represents one monthly trade observation for:

- One reporter country
- One partner market
- One trade flow
- One semiconductor HS code

## Tables

### FACT_SEMICONDUCTOR_TRADE

Stores monthly semiconductor trade measures such as trade value, quantity, and net weight.

### DIM_COUNTRY

Describes reporter and supplier markets. The same dimension is used in two roles: reporter country and partner country.

### DIM_PRODUCT

Describes semiconductor HS codes and broader product categories.

### DIM_DATE

Supports monthly, quarterly, annual, and YTD analysis.

## Data Flow

UN Comtrade  
→ RAW  
→ STAGING  
→ FACT and dimension tables  
→ Executive concentration analysis
