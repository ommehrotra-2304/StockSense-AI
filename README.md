# StockSense AI

**Demand forecasting and inventory decision support using Python, SQL, machine learning, and interactive dashboards.**

StockSense AI is a portfolio project that demonstrates how a retailer could use historical sales to estimate near-term demand, flag potential stockout/overstock situations, and review suggested reorder quantities.

> **Data limitation:** The included demonstration outputs were generated from synthetic retail data. Model metrics and inventory recommendations are for learning and demonstration; they are not verified business outcomes.

## Features

- Generate reproducible synthetic sales, inventory, product, store, and supplier data.
- Clean data and create history-based model features such as sales lags and rolling averages.
- Train a Random Forest regression model to predict daily unit demand.
- Evaluate the model on a later chronological test period and compare it with a previous-week baseline.
- Forecast demand for the next 7 days.
- Estimate inventory coverage and create risk/reorder recommendations.
- Explore risk levels, categories, regions, forecasts, and model metrics in the Streamlit dashboard.
- Export the filtered inventory-action table as CSV.
- Explore sample SQL schema and business queries.

## Technology stack

- **Python:** Pandas, NumPy
- **Machine learning:** scikit-learn RandomForestRegressor
- **Charts:** Altair, Matplotlib, Seaborn
- **Database:** SQLite and SQL
- **Dashboard:** Streamlit
- **Model/data utilities:** joblib

## How the system works

```text
Synthetic retail data
        ↓
Data preparation and feature engineering
        ↓
Historical demand features
        ↓
Random Forest model + chronological evaluation
        ↓
7-day forecast
        ↓
Inventory risk and reorder rules
        ↓
Streamlit dashboard / CSV report
```

## Run locally on Windows

Open the project root in VS Code. The project root is the folder containing `requirements.txt`, `scripts`, `dashboard`, and `data`.

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

The execution-policy command applies only to the current PowerShell session. If the virtual environment is already active, do not create it again.

### 2. Install packages into that environment

```powershell
python -m pip install -r requirements.txt
```

### 3. Rebuild the data, model metrics, forecast, and recommendations

```powershell
python scripts/run_pipeline.py
```

This step regenerates the synthetic raw data and intermediate outputs, trains the model, creates recommendations, and builds a local SQLite database. It can take a little while because the demo contains hundreds of thousands of rows.

### 4. Start the dashboard

```powershell
python -m streamlit run dashboard/app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Dashboard guide

- **Overview:** summary KPIs, risk distribution, demand by category, and priority items.
- **Inventory actions:** filtered risk/action table with CSV export.
- **Demand forecast:** select a product/store pair and review the 7-day forecast.
- **Model quality:** MAE, RMSE, baseline comparison, and model feature importance.

The app uses the small, precomputed `data/processed/forecast_7day.csv`, `data/processed/recommendations.csv`, and `models/metrics.json` files for a quick dashboard start. Larger raw/intermediate files, the local SQLite database, and the trained binary model are excluded from Git tracking; they can be recreated by running the pipeline.

## Model approach and evaluation

The model uses product/store identifiers, price and promotion information, lagged sales, rolling averages, and calendar features. The final period is reserved as a chronological test window so the evaluation simulates forecasting later dates from earlier history.

Metrics:

- **MAE (Mean Absolute Error):** average absolute difference between predicted and actual units.
- **RMSE (Root Mean Squared Error):** gives larger errors more weight.
- **Previous-week baseline:** predicts using sales from the same weekday in the prior week.

The included results are illustrative results on synthetic data only. Performance should be re-tested on a suitable real dataset before making claims about real-world accuracy.

## SQL

- `sql/schema.sql`: sample relational schema.
- `sql/queries.sql`: business questions such as sales summaries and inventory checks.

The pipeline creates `data/stocksense.db` locally; that generated database is not stored in Git.

## Repository structure

```text
StockSense-AI/
├── dashboard/       # Streamlit application and Power BI guide
├── data/
│   └── processed/   # Small dashboard outputs tracked in Git
├── models/          # Metrics and feature importance; model binary is regenerated
├── notebooks/       # Exploration notebook
├── reports/         # Learning notes, project roadmap, interview notes
├── scripts/         # Data, feature, ML, forecast, and database pipeline
├── sql/             # Schema and queries
├── requirements.txt
├── README.md
└── .gitignore
```

## Power BI

`dashboard/POWER_BI_GUIDE.md` explains how to build a Power BI report from the project's data. A `.pbix` dashboard file is not included yet; create and add it as a separate portfolio improvement if Power BI is part of the role you are targeting.

## Responsible interpretation

This is a learning/portfolio demonstration, not an automated purchasing system. Before using a similar model in a real business, validate it on real historical data, account for stockouts and promotions properly, monitor prediction errors, and have business users review reorder actions.
