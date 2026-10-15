from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "model_features.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "product_id_code", "store_id_code", "price", "promotion",
    "lag_1", "lag_7", "lag_14", "rolling_mean_7", "rolling_mean_28",
    "day_of_week", "month", "week_of_year", "day_of_year"
]

Xy = pd.read_csv(DATA, parse_dates=["date"])
Xy = Xy.sort_values("date")
cutoff = Xy["date"].max() - pd.Timedelta(days=30)
train = Xy[Xy["date"] < cutoff]
test = Xy[Xy["date"] >= cutoff]
X_train, y_train = train[FEATURES], train["units_sold"]
X_test, y_test = test[FEATURES], test["units_sold"]

model = RandomForestRegressor(
    n_estimators=45,
    max_depth=12,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)
model.fit(X_train, y_train)
pred = np.clip(model.predict(X_test), 0, None)

mae = mean_absolute_error(y_test, pred)
rmse = mean_squared_error(y_test, pred) ** 0.5
naive = test["lag_7"].clip(lower=0)
naive_mae = mean_absolute_error(y_test, naive)

joblib.dump(model, MODEL_DIR / "demand_model.joblib")
metadata = {
    "model": "RandomForestRegressor",
    "cutoff_date": cutoff.strftime("%Y-%m-%d"),
    "test_days": 30,
    "mae": round(float(mae), 3),
    "rmse": round(float(rmse), 3),
    "naive_weekly_mae": round(float(naive_mae), 3),
    "feature_columns": FEATURES,
}
with open(MODEL_DIR / "metrics.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

fi = pd.DataFrame({"feature": FEATURES, "importance": model.feature_importances_}).sort_values("importance", ascending=False)
fi.to_csv(MODEL_DIR / "feature_importance.csv", index=False)

print(json.dumps(metadata, indent=2))
