-- 1. Top 10 products by units sold
SELECT p.product_name, p.category, SUM(s.units_sold) AS total_units
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_units DESC
LIMIT 10;

-- 2. Sales by month
SELECT strftime('%Y-%m', date) AS month, SUM(units_sold) AS total_units
FROM sales
GROUP BY month
ORDER BY month;

-- 3. Products with stockout days
SELECT product_id, store_id, COUNT(*) AS stockout_days
FROM inventory
WHERE inventory_units = 0
GROUP BY product_id, store_id
HAVING stockout_days > 0
ORDER BY stockout_days DESC;

-- 4. Current high-risk products
SELECT product_id, product_name, store_name, inventory_units,
       ROUND(forecast_7d, 1) AS forecast_7d, risk_level, reorder_qty
FROM recommendations
WHERE risk_level IN ('Critical', 'High')
ORDER BY reorder_qty DESC;

-- 5. Inventory aging proxy: products with >30 days of cover
SELECT product_id, product_name, store_name,
       ROUND(days_of_cover, 1) AS days_of_cover, risk_level
FROM recommendations
WHERE risk_level = 'Overstock'
ORDER BY days_of_cover DESC;

-- 6. Revenue by region
SELECT st.region, ROUND(SUM(s.units_sold * s.price), 2) AS revenue
FROM sales s
JOIN stores st ON st.store_id = s.store_id
GROUP BY st.region
ORDER BY revenue DESC;
