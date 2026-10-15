DROP TABLE IF EXISTS recommendations;
DROP TABLE IF EXISTS forecast_7day;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS product_supplier;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    base_demand INTEGER NOT NULL
);

CREATE TABLE stores (
    store_id TEXT PRIMARY KEY,
    store_name TEXT NOT NULL,
    location TEXT NOT NULL,
    region TEXT NOT NULL,
    store_factor REAL NOT NULL
);

CREATE TABLE suppliers (
    supplier_id TEXT PRIMARY KEY,
    supplier_name TEXT NOT NULL,
    lead_time_days INTEGER NOT NULL,
    min_order_qty INTEGER NOT NULL
);

CREATE TABLE product_supplier (
    product_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    safety_days INTEGER NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE sales (
    date TEXT NOT NULL,
    product_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    units_sold INTEGER NOT NULL,
    price REAL NOT NULL,
    promotion INTEGER NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(store_id) REFERENCES stores(store_id)
);

CREATE TABLE inventory (
    date TEXT NOT NULL,
    product_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    inventory_units INTEGER NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(store_id) REFERENCES stores(store_id)
);

CREATE TABLE forecast_7day (
    date TEXT NOT NULL,
    product_id TEXT NOT NULL,
    store_id TEXT NOT NULL,
    predicted_units REAL NOT NULL
);

CREATE TABLE recommendations (
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    store_id TEXT NOT NULL,
    store_name TEXT NOT NULL,
    location TEXT NOT NULL,
    region TEXT NOT NULL,
    inventory_units INTEGER NOT NULL,
    forecast_7d REAL NOT NULL,
    avg_daily_forecast REAL NOT NULL,
    days_of_cover REAL NOT NULL,
    lead_time_days INTEGER NOT NULL,
    safety_days INTEGER NOT NULL,
    target_stock REAL NOT NULL,
    reorder_qty INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    action TEXT NOT NULL
);
