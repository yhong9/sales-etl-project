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
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the ETL pipeline:

```bash
python scripts/main.py
```

Run the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

## Outputs

The pipeline generates:

- Clean sales data
- Data quality report
- Rejected records
- Rejected records grouped by error type

## Dashboard Metrics

The dashboard includes:

- Monthly revenue trend
- Revenue by region
- Total revenue
- Total profit
- Total orders

## Project Summary

This project demonstrates a complete ETL workflow, including data extraction, data validation, transformation, rejected record handling, and dashboard reporting. It is designed as a portfolio project to show practical skills in Python, pandas, data quality checks, and business analytics.