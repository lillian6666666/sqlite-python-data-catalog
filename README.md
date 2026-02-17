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
   - missing valuessource venv/bin/activate

5. Run basic data quality checks (validation)
6. Export results to output files

## Notes SQL
To open the sqlite, type in 

Demo 1: 
SELECT Date, Open, Close
FROM clean
LIMIT 5;
(shows 5 examples)

Demo 2:
SELECT
    AVG(Close) AS avg_close,
    MAX(Close) AS highest_close,
    MIN(Close) AS lowest_close
FROM clean;
(use SQL to summarize historical data)

Demo 3:
SELECT Date, Close
FROM clean
ORDER BY Close DESC
LIMIT 1;
(which day is highest close?)

## Notes2: 
Because daily return = (today close - yesterday close) / yesterday close
cd ~/Desktop/"SQLPython Project"/sqlite-python-data-catalog
cd sqlite-python-data-catalog
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/build_catalog.py
ls output

 





