# Olist E-Commerce ETL and Analytics

An end-to-end portfolio project that loads the Brazilian E-Commerce Public
Dataset by Olist into PostgreSQL, validates and transforms the data, builds
analytics marts, and serves an interactive Streamlit dashboard.

This is an independent educational project. It is not affiliated with,
sponsored by, or endorsed by Olist.

## Architecture

```text
Olist CSV files
      |
      v
PostgreSQL Raw
      |
      v
Typed and validated Staging
      |
      v
Sales and Review Marts
      |
      v
Streamlit Analytics Dashboard
```

The orchestrated pipeline contains 18 load, quality, transformation, and Mart
build steps. Pipeline executions are recorded in `audit.pipeline_runs` with
status, duration, completed steps, and failure information.

## Dashboard

- Executive overview with business insights and recommendations
- Sales analysis by period, state, and product category
- Customer review sentiment and delivery-performance analysis
- Data quality checks and Raw-to-Staging reconciliation
- Pipeline run monitoring
- Governed Mart data preview, search, and CSV export

## Data Quality

The project checks:

- Missing and duplicate business keys
- Invalid dates, prices, freight values, states, and review scores
- Unmatched customers, orders, and products
- Delivered orders with missing delivery results
- Unknown and untranslated product categories
- Multiple reviews for the same order
- Row-count reconciliation across warehouse layers

## Technology

- Python and pandas
- PostgreSQL
- SQLAlchemy and psycopg
- Streamlit
- Plotly

## Project Structure

```text
sales-etl-project/
|-- .streamlit/
|   `-- config.toml
|-- dashboard/
|   |-- assets/
|   `-- olist_app.py
|-- data/
|   `-- archive/                 # Local source CSV files; ignored by Git
|-- scripts/
|   `-- olist/
|       |-- load_raw_*.py
|       |-- quality_raw_*.py
|       |-- build_staging_*.py
|       |-- build_fact_sales.py
|       |-- build_sales_marts.py
|       |-- build_review_marts.py
|       `-- run_pipeline.py
|-- .env.example
|-- requirements.txt
`-- README.md
```

## Local Setup

1. Create and activate a virtual environment.

2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Create a PostgreSQL database named `olist_warehouse`, then create these
   schemas:

   ```sql
   CREATE SCHEMA IF NOT EXISTS raw;
   CREATE SCHEMA IF NOT EXISTS staging;
   CREATE SCHEMA IF NOT EXISTS mart;
   ```

4. Copy `.env.example` to `.env` and enter the local PostgreSQL credentials.
   Never commit `.env`.

5. Place the Olist CSV files in `data/archive/`. The source data is not stored
   in this repository.

6. Run the complete pipeline:

   ```powershell
   python scripts/olist/run_pipeline.py
   ```

7. Start the dashboard from the project root:

   ```powershell
   python -m streamlit run dashboard/olist_app.py
   ```

## Important Metric Definitions

- Sales includes product price and excludes freight unless explicitly labeled
  as transaction value.
- Sales reporting uses delivered orders.
- Average order sales equals product sales divided by distinct orders.
- Customers are counted with `customer_unique_id`.
- Reviews 1-2 are Negative, 3 is Neutral, and 4-5 are Positive.
- Late delivery means the actual customer delivery date is after the estimated
  delivery date.

## Data Limitations

Data coverage for 2016 is incomplete. The dashboard prevents KPI comparisons
when the comparison period is not fully represented in the dataset.
