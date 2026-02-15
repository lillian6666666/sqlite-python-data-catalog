# sqlite-python-data-catalog
SQL + Python data catalog and lineage mini project

# SQLite + Python Data Catalog Project

## Overview
This project aims to demonstrate a data catalog and data quality pipeline built using **Python** and **SQLite**.

The goal of the project is to simulate core data architecture tasks such as:
- Data into SQL tables
- Metadata generation (data dictionary)
- Data quality checks (validation)
- Simple data lineage tracking

raw data  →  SQL tables  →  clean data  →  reports

## Tech Skills Involved
- Python 3
- SQLite
- Pandas
- VS Code
- Git / GitHub

## Project Structure
- data/ # raw input data
- output/ # generated outputs (metadata, reports)
- src/ # Python scripts

## Workflow
1. Load raw dataset (CSV)
2. Store data in SQLite table 
3. Apply cleaning/transformation 
4. Generate data dictionary:
   - column names
   - data types
   - missing values
5. Run basic data quality checks (validation)
6. Export results to output files


