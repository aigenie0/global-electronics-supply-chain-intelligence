USE ROLE SYSADMIN;

-- Create project's main database.
CREATE DATABASE IF NOT EXISTS SEMICONDUCTOR_SUPPLY_CHAIN_DB
    COMMENT = 'Public-data platform for semiconductor supply-chain analysis';

-- Create raw source-data layer.
CREATE SCHEMA IF NOT EXISTS SEMICONDUCTOR_SUPPLY_CHAIN_DB.RAW
    COMMENT = 'Source data retained close to its original structure';

-- Create data-cleaning and standardization layer.
CREATE SCHEMA IF NOT EXISTS SEMICONDUCTOR_SUPPLY_CHAIN_DB.STAGING
    COMMENT = 'Cleaned and standardized semiconductor trade data';

-- Create business-ready analytics layer.
CREATE SCHEMA IF NOT EXISTS SEMICONDUCTOR_SUPPLY_CHAIN_DB.ANALYTICS
    COMMENT = 'Business-ready tables and executive supply-chain metrics';

-- Create compute resources used to process project queries.
CREATE WAREHOUSE IF NOT EXISTS SEMICONDUCTOR_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'X-Small compute warehouse for the semiconductor project';

-- Set active project context.
USE WAREHOUSE SEMICONDUCTOR_WH;
USE DATABASE SEMICONDUCTOR_SUPPLY_CHAIN_DB;
USE SCHEMA RAW;
