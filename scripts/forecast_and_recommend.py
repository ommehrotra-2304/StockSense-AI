from pathlib import Path
import math
import json
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"

model = joblib.load(MODEL_DIR / "demand_model.joblib")
meta = json.loads((MODEL_DIR / "metrics.json").read_text())
products = pd.read_csv(RAW / "products.csv")
stores = pd.read_csv(RAW / "stores.csv")
suppliers = pd.read_csv(RAW / "suppliers.csv")
ps = pd.read_csv(RAW / "product_supplier.csv")
sales = pd.read_csv(RAW / "sales.csv", parse_dates=["date"]).sort_values(["product_id", "store_id", "date"])
inventory = pd.read_csv(RAW / "inventory.csv", parse_dates=["date"]).sort_values(["product_id", "store_id", "date"])

product_codes = {v: i for i, v in enumerate(sorted(sales.product_id.unique()))}
store_codes = {v: i for i, v in enumerate(sorted(sales.store_id.unique()))}
product_price = products.set_index("product_id")["price"].to_dict()
lead = ps.set_index("product_id").join(suppliers.set_index("supplier_id"), on="supplier_id")["lead_time_days"].to_dict()
moq = ps.set_index("product_id").join(suppliers.set_index("supplier_id"), on="supplier_id")["min_order_qty"].to_dict()
safety_days = ps.set_index("product_id")["safety_days"].to_dict()

last_date = sales["date"].max()
history = {(pid, sid): g["units_sold"].tolist() for (pid, sid), g in sales.groupby(["product_id", "store_id"], sort=False)}

records = []
for (pid, sid), hist in history.items():
    vals = hist.copy()
    for step in range(1, 8):
        d = last_date + pd.Timedelta(days=step)
        def lag(n):
            return vals[-n] if len(vals) >= n else float(np.mean(vals))
        rolling7 = float(np.mean(vals[-7:])) if vals else 0.0
        rolling28 = float(np.mean(vals[-28:])) if vals else 0.0
        row = pd.DataFrame([{
            "product_id_code": product_codes[pid],
            "store_id_code": store_codes[sid],
            "price": product_price[pid],
            "promotion": 0,
            "lag_1": lag(1),
            "lag_7": lag(7),
            "lag_14": lag(14),
            "rolling_mean_7": rolling7,
            "rolling_mean_28": rolling28,
            "day_of_week": d.dayofweek,
            "month": d.month,
            "week_of_year": int(d.isocalendar().week),
            "day_of_year": d.dayofyear,
        }])
        pred = float(max(0, model.predict(row[meta["feature_columns"]])[0]))
        vals.append(pred)
        records.append({"date": d, "product_id": pid, "store_id": sid, "predicted_units": pred})

forecast = pd.DataFrame(records)
forecast.to_csv(PROC / "forecast_7day.csv", index=False)

latest_inv = inventory.sort_values("date").groupby(["product_id", "store_id"], as_index=False).tail(1)
seven = forecast.groupby(["product_id", "store_id"], as_index=False)["predicted_units"].sum().rename(columns={"predicted_units": "forecast_7d"})
rec = latest_inv.merge(seven, on=["product_id", "store_id"])
rec = rec.merge(ps, on="product_id", how="left").merge(suppliers[["supplier_id", "lead_time_days", "min_order_qty"]], on="supplier_id", how="left")
rec["avg_daily_forecast"] = rec["forecast_7d"] / 7.0
rec["days_of_cover"] = np.where(rec["avg_daily_forecast"] > 0, rec["inventory_units"] / rec["avg_daily_forecast"], np.inf)
rec["target_stock"] = rec["avg_daily_forecast"] * (rec["lead_time_days"] + rec["safety_days"])
raw_order = (rec["target_stock"] - rec["inventory_units"]).clip(lower=0)
rec["reorder_qty"] = [
    0 if x <= 0 else int(math.ceil(x / moq / 1) * moq)
    for x, moq in zip(raw_order, rec["min_order_qty"])
]

def risk(row):
    if row["forecast_7d"] > 0 and row["inventory_units"] < row["avg_daily_forecast"] * row["lead_time_days"]:
        return "Critical"
    if row["days_of_cover"] < row["lead_time_days"] + row["safety_days"]:
        return "High"
    if row["days_of_cover"] > 30:
        return "Overstock"
    return "Normal"

rec["risk_level"] = rec.apply(risk, axis=1)
rec["action"] = np.select(
    [rec["risk_level"].eq("Critical"), rec["risk_level"].eq("High"), rec["risk_level"].eq("Overstock")],
    ["Reorder Immediately", "Reorder", "Reduce / Hold Orders"],
    default="No Action",
)
rec = rec.merge(products[["product_id", "product_name", "category"]], on="product_id", how="left")
rec = rec.merge(stores[["store_id", "store_name", "location", "region"]], on="store_id", how="left")
cols = ["product_id", "product_name", "category", "store_id", "store_name", "location", "region", "inventory_units", "forecast_7d", "avg_daily_forecast", "days_of_cover", "lead_time_days", "safety_days", "target_stock", "reorder_qty", "risk_level", "action"]
rec[cols].sort_values(["risk_level", "reorder_qty"], ascending=[True, False]).to_csv(PROC / "recommendations.csv", index=False)
print("Created 7-day forecasts and inventory recommendations.")
print(rec["risk_level"].value_counts())
