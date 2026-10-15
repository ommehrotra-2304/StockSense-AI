# Power BI Guide for StockSense AI

Power BI is optional because the repository also includes a Streamlit dashboard. Use these files as data sources:

- `data/raw/products.csv`
- `data/raw/stores.csv`
- `data/raw/sales.csv`
- `data/raw/inventory.csv`
- `data/processed/forecast_7day.csv`
- `data/processed/recommendations.csv`

## Recommended model relationships

- `products[product_id]` → `sales[product_id]`
- `stores[store_id]` → `sales[store_id]`
- `products[product_id]` → `inventory[product_id]`
- `stores[store_id]` → `inventory[store_id]`
- `products[product_id]` → `forecast_7day[product_id]`
- `stores[store_id]` → `forecast_7day[store_id]`
- `products[product_id]` → `recommendations[product_id]`
- `stores[store_id]` → `recommendations[store_id]`

For a beginner build, loading the CSVs into Power BI and creating relationships in Model view is enough.

## Page 1 — Business Overview

Cards:
- Total Revenue = `SUMX(sales, sales[units_sold] * sales[price])`
- Units Sold = `SUM(sales[units_sold])`
- Products = `DISTINCTCOUNT(products[product_id])`
- Stores = `DISTINCTCOUNT(stores[store_id])`

Charts:
- Monthly sales trend
- Revenue by region
- Top 10 products by units sold
- Sales by category

## Page 2 — Inventory Risk

Cards:
- Critical items
- High-risk items
- Overstock items

Table:
- Product
- Store
- Inventory units
- 7-day forecast
- Days of cover
- Risk level
- Reorder quantity
- Action

Add a slicer for `region`, `category`, and `risk_level`.

## Page 3 — Demand Forecast

Use `forecast_7day.csv`.

Recommended visual:
- Line chart with `date` on the X-axis and `predicted_units` on the Y-axis.

Add product and store slicers.

## Page 4 — Reorder Recommendations

Use `recommendations.csv`.

Table columns:
- Product name
- Store name
- Current inventory
- Forecast 7d
- Lead time
- Safety days
- Target stock
- Reorder quantity
- Risk
- Action

Sort by risk and reorder quantity.

## Interview tip

Do not say Power BI "did the prediction." Python/Scikit-learn produced the forecast. Power BI is used to communicate the forecasts, risks, and recommended actions to a business user.
