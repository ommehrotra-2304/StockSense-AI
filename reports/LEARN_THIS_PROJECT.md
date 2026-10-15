# Learn StockSense AI in Simple Words

This file is your study guide. You do not need to memorize every line of code. You need to understand the flow and the reason for each major step.

## 1. What problem are we solving?

A shop can lose money in two opposite ways:

- Too little stock → a customer wants the product but it is unavailable.
- Too much stock → money is stuck in products that are not selling quickly.

StockSense AI tries to predict near-future demand and turn that prediction into a simple inventory action.

## 2. What is our input?

The project uses synthetic data that behaves like retail data. Every sales row contains a date, product, store, price, promotion flag, and units sold. Inventory rows track remaining units.

Because the data is synthetic, the project is reproducible and safe to share on GitHub. In a stronger second version, you can replace it with a public retail dataset.

## 3. What does Pandas do?

Pandas is the main tool for working with tables in Python. In this project it is used to read CSV files, clean data, join tables, group data, and create new columns.

Think of Pandas as "Excel-style data work using Python code."

## 4. What is a feature?

A feature is information given to a machine-learning model to help it make a prediction.

Example:

- yesterday's sales
- sales 7 days ago
- average sales in the last 7 days
- day of week
- month
- product id

The model sees these features and tries to predict the next sales value.

## 5. What is a lag?

A lag is an older value used as a clue about the future.

`lag_1` = sales yesterday.

`lag_7` = sales 7 days ago.

`lag_14` = sales 14 days ago.

Why can this help? Because retail demand often has patterns. For example, a product may sell more on weekends than weekdays.

## 6. What is a rolling average?

A rolling average is a recent average.

`rolling_mean_7` means the average sales across the previous 7 days.

It smooths out noisy day-to-day changes and gives the model a sense of the recent level of demand.

## 7. Why not randomly split the data?

For a normal classification problem, random splitting can be fine. Forecasting is different because time has an order.

We train on earlier dates and test on later dates. This is meant to imitate the real situation: use the past to predict the future.

## 8. What is Random Forest?

Random Forest is an ML method that builds many decision trees and combines their predictions.

One tree might make a rough prediction. Many trees can reduce the effect of an individual tree being wrong.

In this project we use it because the input is tabular and contains relationships that may not be perfectly linear.

## 9. What is regression?

Regression means predicting a number.

Our target is `units_sold`, so this is a regression problem.

## 10. What are MAE and RMSE?

MAE = average absolute prediction error.

If MAE is about 7, it means the model's predictions are off by roughly 7 units on average on the test data.

RMSE also measures error, but it gives more penalty to bigger mistakes.

Lower is better.

## 11. What is the baseline?

A baseline is a simple method used for comparison.

Our baseline uses the sales from 7 days earlier as the prediction.

If the ML model cannot beat a very simple baseline, the model may not be useful.

On the generated test set, the current model produced:

- MAE: 6.952
- RMSE: 9.031
- Weekly naive MAE: 10.572

These results describe this synthetic dataset only. They should not be presented as proof of real-world accuracy.

## 12. What is a 7-day forecast?

The model predicts demand for each of the next 7 days. We then add those predictions to estimate the total expected demand over the next week.

## 13. What is lead time?

Lead time is how many days a supplier needs to deliver an order.

Example: if lead time is 5 days, an order placed today may arrive in about 5 days.

That matters because the shop must have enough stock to survive until the new shipment arrives.

## 14. What is safety stock?

Safety stock is an extra buffer of inventory kept to protect against demand being higher than expected or deliveries taking longer than planned.

Our demo represents this simply with a number of safety days per product.

## 15. How do we calculate a reorder recommendation?

First:

`average_daily_forecast = 7_day_forecast / 7`

Then:

`target_stock = average_daily_forecast × (lead_time_days + safety_days)`

Then compare target stock with current inventory.

If current inventory is too low, the system recommends an order.

## 16. Why round the order quantity?

Suppliers may require minimum order quantities. If the calculated quantity is 37 but the supplier only accepts multiples of 20, we round up to 40.

## 17. What does the risk engine do?

It converts numbers into simple business language:

- Critical
- High
- Normal
- Overstock

Then it produces an action such as:

- Reorder Immediately
- Reorder
- No Action
- Reduce / Hold Orders

## 18. Why use SQL?

SQL is useful when data lives in a database and a business user asks questions such as:

"What are the top-selling products?"

"Which products had stockouts?"

"Which region generated the most revenue?"

The project stores the main tables in SQLite so the SQL layer can be demonstrated independently from Python.

## 19. What does Power BI do?

Python/ML creates the forecasts and recommendations.

Power BI turns those outputs into an easy-to-read business dashboard.

A good interview sentence is:

"Python performs the data preparation and forecasting, while Power BI communicates the results and supports business decisions."

## 20. What are the major limitations?

Be honest about them:

1. The current data is synthetic.
2. Future promotion information is assumed to be zero in the forecast.
3. The reorder logic is intentionally simple.
4. The demo does not model every real-world cost or supplier constraint.
5. A production system would need monitoring and regular retraining.

A good project is easier to defend when you understand its limitations.
