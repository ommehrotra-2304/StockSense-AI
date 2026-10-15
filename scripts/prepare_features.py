from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

sales = pd.read_csv(RAW / "sales.csv", parse_dates=["date"])
products = pd.read_csv(RAW / "products.csv")
stores = pd.read_csv(RAW / "stores.csv")

sales = sales.merge(products, on=["product_id"], suffixes=("", "_product"))
sales = sales.merge(stores[["store_id", "region", "store_factor"]], on="store_id", how="left")
sales = sales.sort_values(["product_id", "store_id", "date"])

g = sales.groupby(["product_id", "store_id"], group_keys=False)
sales["lag_1"] = g["units_sold"].shift(1)
sales["lag_7"] = g["units_sold"].shift(7)
sales["lag_14"] = g["units_sold"].shift(14)
sales["rolling_mean_7"] = g["units_sold"].transform(lambda s: s.shift(1).rolling(7).mean())
sales["rolling_mean_28"] = g["units_sold"].transform(lambda s: s.shift(1).rolling(28).mean())
sales["day_of_week"] = sales["date"].dt.dayofweek
sales["month"] = sales["date"].dt.month
sales["week_of_year"] = sales["date"].dt.isocalendar().week.astype(int)
sales["day_of_year"] = sales["date"].dt.dayofyear

for col in ["product_id", "store_id"]:
    sales[f"{col}_code"] = sales[col].astype("category").cat.codes

features = sales.dropna().copy()
features.to_csv(PROC / "model_features.csv", index=False)
sales.to_csv(PROC / "sales_enriched.csv", index=False)
print(f"Prepared {len(features):,} training rows.")
