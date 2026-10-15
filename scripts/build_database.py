from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
DB = ROOT / "data" / "stocksense.db"

conn = sqlite3.connect(DB)
with open(ROOT / "sql" / "schema.sql", encoding="utf-8") as f:
    conn.executescript(f.read())

tables = {
    "products": "products.csv",
    "stores": "stores.csv",
    "suppliers": "suppliers.csv",
    "product_supplier": "product_supplier.csv",
    "sales": "sales.csv",
    "inventory": "inventory.csv",
}
for table, filename in tables.items():
    pd.read_csv(RAW / filename).to_sql(table, conn, if_exists="append", index=False)

pd.read_csv(PROC / "forecast_7day.csv").to_sql("forecast_7day", conn, if_exists="append", index=False)
pd.read_csv(PROC / "recommendations.csv").to_sql("recommendations", conn, if_exists="append", index=False)
conn.close()
print(f"SQLite database created at {DB}")
