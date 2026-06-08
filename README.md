# Sales ETL Pipeline Project

This project is a Python-based ETL pipeline for sales data. It extracts raw CSV files, validates data quality, transforms and joins sales, customer, and product data, and generates clean outputs for analysis. The project also includes a Streamlit dashboard to visualize key sales metrics.

## Project Features

- Extract raw sales, customer, and product data from CSV files
- Validate raw data quality
- Detect duplicate IDs, missing values, invalid dates, and negative values
- Generate data quality reports
- Save rejected records by error type
- Transform and join sales data
- Calculate revenue, cost, profit, and profit margin
- Build an interactive Streamlit dashboard

## Tools Used

- Python
- pandas
- Streamlit
- Plotly
- Git and GitHub

## Project Structure

```text
sales-etl-project/
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   └── main.py
├── dashboard/
│   └── app.py
├── requirements.txt
├── README.md
└── .gitignore

<img width="826" height="804" alt="image" src="https://github.com/user-attachments/assets/deb88d1b-ca09-4160-aa63-701432a92180" />
