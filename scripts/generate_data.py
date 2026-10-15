from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(42)

START = "2024-01-01"
END = "2025-12-31"
DATES = pd.date_range(START, END, freq="D")

categories = ["Beverages", "Snacks", "Grocery", "Personal Care", "Household"]
regions = ["North", "South", "East", "West", "Central", "NCR"]

products = []
for i in range(1, 51):
    cat = categories[(i - 1) % len(categories)]
    products.append({
        "product_id": f"P{i:03d}",
        "product_name": f"{cat.replace(' ', '')} Product {i:03d}",
        "category": cat,
        "price": round(float(RNG.uniform(20, 900)), 2),
        "base_demand": int(RNG.integers(12, 80)),
    })
products = pd.DataFrame(products)

stores = pd.DataFrame([
    {"store_id": "S001", "store_name": "Kanpur Central", "location": "Kanpur", "region": "North", "store_factor": 1.10},
    {"store_id": "S002", "store_name": "Lucknow Market", "location": "Lucknow", "region": "North", "store_factor": 1.20},
    {"store_id": "S003", "store_name": "Delhi Hub", "location": "Delhi", "region": "NCR", "store_factor": 1.45},
    {"store_id": "S004", "store_name": "Jaipur Outlet", "location": "Jaipur", "region": "West", "store_factor": 0.90},
    {"store_id": "S005", "store_name": "Kolkata Point", "location": "Kolkata", "region": "East", "store_factor": 1.00},
    {"store_id": "S006", "store_name": "Bengaluru Store", "location": "Bengaluru", "region": "South", "store_factor": 1.30},
])

supplier_rows = []
for i, p in products.iterrows():
    supplier_rows.append({
        "supplier_id": f"SUP{(i % 10) + 1:03d}",
        "supplier_name": f"Supplier {(i % 10) + 1:03d}",
        "lead_time_days": int(RNG.integers(2, 8)),
        "min_order_qty": int(RNG.choice([10, 20, 30, 50])),
    })
suppliers = pd.DataFrame(supplier_rows).drop_duplicates("supplier_id")
product_supplier = products[["product_id"]].copy()
product_supplier["supplier_id"] = [f"SUP{((i) % 10) + 1:03d}" for i in range(len(products))]
product_supplier["safety_days"] = RNG.integers(2, 6, size=len(products))
product_supplier = product_supplier.merge(suppliers, on="supplier_id", how="left")

# Build demand first, then simulate inventory/replenishment.
rows = []
for p in products.itertuples(index=False):
    for s in stores.itertuples(index=False):
        product_factor = RNG.uniform(0.85, 1.15)
        for d in DATES:
            dow = d.dayofweek
            month = d.month
            weekend_factor = 1.15 if dow in (4, 5, 6) else 1.0
            # Seasonal demand: stronger around summer + year-end, with small long-term trend.
            season = 1 + 0.12 * np.sin(2 * np.pi * (d.dayofyear / 365.25))
            if month in (11, 12):
                season *= 1.12
            if month in (4, 5, 6):
                season *= 1.08
            trend = 1 + 0.00035 * (d - DATES[0]).days
            promotion = int(RNG.random() < 0.06)
            promo_factor = 1.30 if promotion else 1.0
            lam = max(1, p.base_demand * s.store_factor * product_factor * weekend_factor * season * trend * promo_factor)
            demand = int(RNG.poisson(lam))
            rows.append({
                "date": d,
                "product_id": p.product_id,
                "store_id": s.store_id,
                "price": p.price,
                "promotion": promotion,
                "demand_units": demand,
            })

demand = pd.DataFrame(rows)
demand["date"] = pd.to_datetime(demand["date"])

# Inventory simulation. Orders arrive after supplier lead time.
orders = {}
inventory_rows = []
actual_sales = []
sp = product_supplier.set_index("product_id").to_dict("index")

for (pid, sid), grp in demand.groupby(["product_id", "store_id"], sort=False):
    meta = sp[pid]
    lead = int(meta["lead_time_days"])
    safety_days = int(meta["safety_days"])
    moq = int(meta["min_order_qty"])
    grp = grp.sort_values("date")
    inv = int(RNG.integers(80, 220))
    pending = {}
    recent_demand = []
    for r in grp.itertuples(index=False):
        arrivals = pending.pop(r.date, 0)
        inv += arrivals
        sold = min(inv, int(r.demand_units))
        inv -= sold
        actual_sales.append((r.date, pid, sid, sold, r.price, r.promotion))
        recent_demand.append(int(r.demand_units))
        if len(recent_demand) > 14:
            recent_demand.pop(0)
        avg14 = float(np.mean(recent_demand)) if recent_demand else float(r.demand_units)
        reorder_point = avg14 * lead + avg14 * safety_days
        if inv <= reorder_point and r.date < DATES[-1] - pd.Timedelta(days=lead):
            qty = max(moq, int(np.ceil(avg14 * (lead + safety_days))))
            arrival_date = r.date + pd.Timedelta(days=lead)
            pending[arrival_date] = pending.get(arrival_date, 0) + qty
        inventory_rows.append((r.date, pid, sid, inv))

sales = pd.DataFrame(actual_sales, columns=["date", "product_id", "store_id", "units_sold", "price", "promotion"])
inventory = pd.DataFrame(inventory_rows, columns=["date", "product_id", "store_id", "inventory_units"])

sales.to_csv(OUT / "sales.csv", index=False)
inventory.to_csv(OUT / "inventory.csv", index=False)
products.to_csv(OUT / "products.csv", index=False)
stores.to_csv(OUT / "stores.csv", index=False)
suppliers.to_csv(OUT / "suppliers.csv", index=False)
product_supplier[["product_id", "supplier_id", "safety_days"]].to_csv(OUT / "product_supplier.csv", index=False)

print(f"Generated {len(sales):,} sales rows and {len(inventory):,} inventory rows.")
print(f"Output: {OUT}")
