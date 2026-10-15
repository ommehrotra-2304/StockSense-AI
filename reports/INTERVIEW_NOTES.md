# StockSense AI — Interview Notes

## 30-second explanation

StockSense AI predicts short-term product demand and turns that prediction into inventory actions. The system uses Python for data processing and model training, SQLite/SQL for business analysis and storage, Scikit-learn for machine learning, and Streamlit/Power BI for reporting.

## Common questions

### Why did you build this project?
Retail businesses can lose sales when products are unavailable and money when too much stock sits unused. I wanted to build a system that moves from historical sales data to a practical inventory recommendation.

### Why Random Forest?
It is a strong baseline for tabular data, handles nonlinear relationships, and is relatively easy to inspect. I did not assume it was the best model; I compared it with a simple weekly baseline and would compare gradient boosting/time-series models next.

### What is a lag feature?
It is a previous value used to help predict a future value. For example, `lag_7` means the sales from 7 days earlier.

### Why use a time-based split?
Randomly mixing past and future rows can leak future information into training. A chronological split better represents the real task: training on the past and predicting the future.

### What is MAE?
Mean Absolute Error is the average absolute difference between the prediction and the real value. Lower is better, and it is easy to explain in business units.

### What is RMSE?
Root Mean Squared Error penalizes larger mistakes more strongly than MAE. Lower is better.

### What does the model predict?
Daily units sold for a product-store pair.

### How did you convert a prediction into a reorder recommendation?
I estimated average daily demand from the 7-day forecast, considered supplier lead time and a safety buffer, and compared the resulting target stock with current inventory. The order quantity is rounded to the supplier's minimum order quantity.

### What is the limitation?
The demo uses synthetic data, assumes future promotions are unknown/zero, and uses simple inventory rules. A production system would need real demand history, holiday effects, supplier constraints, costs, and model monitoring.
