from pathlib import Path
import json

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"

RISK_ORDER = ["Critical", "High", "Normal", "Overstock"]
RISK_COLORS = ["#B91C1C", "#EA580C", "#16A34A", "#64748B"]

st.set_page_config(
    page_title="StockSense AI | Inventory Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Small amount of CSS to improve hierarchy while keeping Streamlit's native controls.
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.8rem; padding-bottom: 2.5rem; }
      .main-title { font-size: 2.4rem; font-weight: 750; letter-spacing: -0.04em; margin-bottom: 0.15rem; }
      .subtitle { color: #9CA3AF; font-size: 1rem; margin-bottom: 1.1rem; }
      div[data-testid="stMetric"] { border: 1px solid rgba(128,128,128,.22); padding: 14px 16px; border-radius: 12px; }
      .demo-note { border-left: 4px solid #3B82F6; padding: 10px 14px; background: rgba(59,130,246,.09); border-radius: 5px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data():
    required = [
        PROC / "recommendations.csv",
        PROC / "forecast_7day.csv",
        MODEL_DIR / "metrics.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Required project output files are missing: " + ", ".join(missing)
            + ". Run `python scripts/run_pipeline.py` from the project root first."
        )

    recommendations = pd.read_csv(PROC / "recommendations.csv")
    forecasts = pd.read_csv(PROC / "forecast_7day.csv", parse_dates=["date"])
    metrics = json.loads((MODEL_DIR / "metrics.json").read_text(encoding="utf-8"))

    recommendations["risk_level"] = recommendations["risk_level"].astype(str)
    for col in ["inventory_units", "forecast_7d", "days_of_cover", "reorder_qty"]:
        recommendations[col] = pd.to_numeric(recommendations[col], errors="coerce").fillna(0)
    forecasts["predicted_units"] = pd.to_numeric(forecasts["predicted_units"], errors="coerce").fillna(0)
    return recommendations, forecasts, metrics


try:
    rec, fc, metrics = load_data()
except Exception as exc:
    st.error("StockSense AI could not load its output files.")
    st.exception(exc)
    st.stop()

# ------------------------------- Sidebar filters -------------------------------
st.sidebar.markdown("## Filters")
st.sidebar.caption("Filters apply to the overview, risk table, and forecast choices.")
regions = ["All regions"] + sorted(rec["region"].dropna().unique().tolist())
categories = ["All categories"] + sorted(rec["category"].dropna().unique().tolist())

selected_region = st.sidebar.selectbox("Region", regions)
selected_category = st.sidebar.selectbox("Product category", categories)
selected_risks = st.sidebar.multiselect("Risk level", RISK_ORDER, default=RISK_ORDER)
search_term = st.sidebar.text_input("Find product or store", placeholder="e.g. Beverages or Kanpur")
st.sidebar.divider()
st.sidebar.caption("Dataset: synthetic retail demonstration data")

view = rec.copy()
if selected_region != "All regions":
    view = view[view["region"] == selected_region]
if selected_category != "All categories":
    view = view[view["category"] == selected_category]
if selected_risks:
    view = view[view["risk_level"].isin(selected_risks)]
else:
    view = view.iloc[0:0]
if search_term.strip():
    needle = search_term.strip().casefold()
    mask = (
        view["product_name"].astype(str).str.casefold().str.contains(needle, na=False)
        | view["store_name"].astype(str).str.casefold().str.contains(needle, na=False)
    )
    view = view[mask]

view = view.copy()
view["_risk_order"] = view["risk_level"].map({risk: i for i, risk in enumerate(RISK_ORDER)}).fillna(99)
view = view.sort_values(["_risk_order", "reorder_qty"], ascending=[True, False])

# ----------------------------------- Header ------------------------------------
st.markdown('<div class="main-title">📦 StockSense AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Demand forecasting and inventory decision support</div>',
    unsafe_allow_html=True,
)
forecast_start = fc["date"].min().strftime("%d %b %Y") if not fc.empty else "—"
forecast_end = fc["date"].max().strftime("%d %b %Y") if not fc.empty else "—"
st.caption(f"Forecast window: {forecast_start} – {forecast_end}  ·  Showing {len(view):,} product–store combinations after filters")

if view.empty:
    st.warning("No rows match the selected filters. Change the region, category, risk level, or search text.")
    st.stop()

# ------------------------------------ KPIs -------------------------------------
products_count = view["product_id"].nunique()
inventory_units = int(view["inventory_units"].sum())
forecast_units = int(view["forecast_7d"].sum())
high_critical = int(view["risk_level"].isin(["High", "Critical"]).sum())
reorder_pairs = int(view["action"].astype(str).str.contains("Reorder", case=False, na=False).sum())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Products represented", f"{products_count:,}", help="Unique products represented in the filtered product–store rows.")
k2.metric("Inventory on hand", f"{inventory_units:,} units")
k3.metric("Expected demand · 7 days", f"{forecast_units:,} units")
k4.metric("High / critical risk", f"{high_critical:,}", help="Count of filtered product–store combinations marked High or Critical.")

# ------------------------------------ Tabs -------------------------------------
tab_overview, tab_risk, tab_forecast, tab_model = st.tabs(
    ["Overview", "Inventory actions", "Demand forecast", "Model quality"]
)

with tab_overview:
    st.subheader("Inventory health at a glance")
    left, right = st.columns([1, 1.25], gap="large")

    with left:
        st.markdown("#### Risk distribution")
        risk_counts = (
            view["risk_level"].value_counts()
            .reindex(RISK_ORDER, fill_value=0)
            .rename_axis("risk_level")
            .reset_index(name="product_store_pairs")
        )
        risk_chart = (
            alt.Chart(risk_counts)
            .mark_bar(cornerRadiusEnd=5)
            .encode(
                x=alt.X("risk_level:N", sort=RISK_ORDER, title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("product_store_pairs:Q", title="Product–store combinations"),
                color=alt.Color(
                    "risk_level:N", scale=alt.Scale(domain=RISK_ORDER, range=RISK_COLORS),
                    legend=None,
                ),
                tooltip=[alt.Tooltip("risk_level:N", title="Risk"), alt.Tooltip("product_store_pairs:Q", title="Combinations")],
            )
            .properties(height=280)
        )
        st.altair_chart(risk_chart, width="stretch")

    with right:
        st.markdown("#### Expected 7-day demand by category")
        category_summary = (
            view.groupby("category", as_index=False)["forecast_7d"].sum()
            .sort_values("forecast_7d", ascending=False)
        )
        category_chart = (
            alt.Chart(category_summary)
            .mark_bar(cornerRadiusEnd=5, color="#60A5FA")
            .encode(
                y=alt.Y("category:N", sort="-x", title=None),
                x=alt.X("forecast_7d:Q", title="Forecast units"),
                tooltip=[alt.Tooltip("category:N", title="Category"), alt.Tooltip("forecast_7d:Q", title="7-day demand", format=",.1f")],
            )
            .properties(height=280)
        )
        st.altair_chart(category_chart, width="stretch")

    st.subheader("Highest-priority inventory actions")
    priority = view[view["risk_level"].isin(["Critical", "High"])].head(8)
    if priority.empty:
        st.success("No High or Critical items in the current filter selection.")
    else:
        st.dataframe(
            priority[["product_name", "store_name", "inventory_units", "forecast_7d", "days_of_cover", "risk_level", "reorder_qty", "action"]],
            width="stretch",
            hide_index=True,
            column_config={
                "inventory_units": st.column_config.NumberColumn("Stock on hand", format="%d"),
                "forecast_7d": st.column_config.NumberColumn("7-day demand", format="%.1f"),
                "days_of_cover": st.column_config.NumberColumn("Days of cover", format="%.1f"),
                "reorder_qty": st.column_config.NumberColumn("Suggested reorder", format="%d"),
            },
        )

with tab_risk:
    st.subheader("Inventory actions")
    st.write("Prioritized product–store rows based on risk level and suggested reorder quantity.")
    st.caption("Days of cover is the approximate number of days current stock can satisfy forecast demand at the estimated daily rate.")
    risk_table = view.drop(columns=["_risk_order"], errors="ignore").copy()
    risk_table = risk_table[[
        "product_name", "category", "store_name", "region", "inventory_units", "forecast_7d",
        "days_of_cover", "lead_time_days", "risk_level", "reorder_qty", "action",
    ]]
    st.dataframe(
        risk_table,
        width="stretch",
        hide_index=True,
        column_config={
            "inventory_units": st.column_config.NumberColumn("Stock on hand", format="%d"),
            "forecast_7d": st.column_config.NumberColumn("7-day demand", format="%.1f"),
            "days_of_cover": st.column_config.NumberColumn("Days of cover", format="%.1f"),
            "lead_time_days": st.column_config.NumberColumn("Supplier lead time", format="%d"),
            "reorder_qty": st.column_config.NumberColumn("Suggested reorder", format="%d"),
        },
    )
    csv_data = risk_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered inventory report (CSV)",
        data=csv_data,
        file_name="stocksense_inventory_actions.csv",
        mime="text/csv",
    )
    st.caption(f"Showing {len(risk_table):,} rows. Export respects the filters in the sidebar.")

with tab_forecast:
    st.subheader("7-day product demand forecast")
    combinations = (
        view[["product_id", "product_name", "store_id", "store_name"]]
        .drop_duplicates()
        .sort_values(["product_name", "store_name"])
        .reset_index(drop=True)
    )
    combinations["display"] = combinations["product_name"] + " — " + combinations["store_name"]
    selected_display = st.selectbox("Choose a product and store", combinations["display"].tolist())
    selected = combinations.loc[combinations["display"] == selected_display].iloc[0]

    selected_forecast = fc[
        (fc["product_id"] == selected["product_id"])
        & (fc["store_id"] == selected["store_id"])
    ].sort_values("date").copy()
    selected_forecast["date"] = pd.to_datetime(selected_forecast["date"])

    row = view[
        (view["product_id"] == selected["product_id"])
        & (view["store_id"] == selected["store_id"])
    ].iloc[0]
    fm1, fm2, fm3, fm4 = st.columns(4)
    fm1.metric("Current stock", f"{int(row['inventory_units']):,} units")
    fm2.metric("Forecast · 7 days", f"{selected_forecast['predicted_units'].sum():,.1f} units")
    fm3.metric("Days of cover", f"{row['days_of_cover']:.1f} days")
    fm4.metric("Suggested reorder", f"{int(row['reorder_qty']):,} units")

    forecast_chart = (
        alt.Chart(selected_forecast)
        .mark_line(point=True, strokeWidth=3, color="#60A5FA")
        .encode(
            x=alt.X("date:T", title="Forecast date", axis=alt.Axis(format="%b %d", labelAngle=0, tickCount=7)),
            y=alt.Y("predicted_units:Q", title="Predicted units", scale=alt.Scale(zero=True)),
            tooltip=[alt.Tooltip("date:T", title="Date", format="%A, %b %d"), alt.Tooltip("predicted_units:Q", title="Predicted units", format=",.1f")],
        )
        .properties(height=360)
    )
    st.altair_chart(forecast_chart, width="stretch")
    with st.expander("View forecast values"):
        display_forecast = selected_forecast.rename(columns={"date": "Forecast date", "predicted_units": "Predicted units"})
        st.dataframe(display_forecast, width="stretch", hide_index=True)

    if row["risk_level"] == "Critical":
        st.error(f"Recommended action: {row['action']}. Current inventory may not cover demand during supplier lead time.")
    elif row["risk_level"] == "High":
        st.warning(f"Recommended action: {row['action']}. Review the suggested order against supplier minimums and local requirements.")
    elif row["risk_level"] == "Overstock":
        st.info(f"Recommended action: {row['action']}. Consider holding or reducing the next order until stock falls.")
    else:
        st.success(f"Recommended action: {row['action']}. No immediate inventory intervention is flagged by the current rules.")

with tab_model:
    st.subheader("Model quality")
    model_name = metrics.get("model", "Forecasting model")
    st.caption(f"Model: {model_name} · Test window: {metrics.get('test_days', '—')} days · Training cutoff: {metrics.get('cutoff_date', '—')}")
    mae = float(metrics.get("mae", 0))
    rmse = float(metrics.get("rmse", 0))
    baseline = float(metrics.get("naive_weekly_mae", 0))
    improvement = ((baseline - mae) / baseline * 100) if baseline else 0
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("MAE", f"{mae:.3f}", help="Mean Absolute Error: average absolute difference between predictions and actual units sold.")
    q2.metric("RMSE", f"{rmse:.3f}", help="Root Mean Squared Error: penalizes larger prediction errors more strongly.")
    q3.metric("Weekly baseline MAE", f"{baseline:.3f}", help="A simple benchmark using the same weekday from the previous week.")
    q4.metric("MAE improvement vs baseline", f"{improvement:.1f}%" if baseline else "—")

    compare = pd.DataFrame({"method": ["Random Forest", "Previous-week baseline"], "mae": [mae, baseline]})
    compare_chart = (
        alt.Chart(compare)
        .mark_bar(cornerRadiusEnd=5)
        .encode(
            x=alt.X("mae:Q", title="MAE · lower is better"),
            y=alt.Y("method:N", sort="-x", title=None),
            color=alt.Color("method:N", scale=alt.Scale(domain=["Random Forest", "Previous-week baseline"], range=["#60A5FA", "#9CA3AF"]), legend=None),
            tooltip=[alt.Tooltip("method:N", title="Method"), alt.Tooltip("mae:Q", title="MAE", format=".3f")],
        )
        .properties(height=170)
    )
    st.altair_chart(compare_chart, width="stretch")

    importance_path = MODEL_DIR / "feature_importance.csv"
    if importance_path.exists():
        importance = pd.read_csv(importance_path)
        if not importance.empty and {"feature", "importance"}.issubset(importance.columns):
            st.markdown("#### Most influential model features")
            top_features = importance.sort_values("importance", ascending=False).head(10).sort_values("importance")
            feature_chart = (
                alt.Chart(top_features)
                .mark_bar(cornerRadiusEnd=4, color="#34D399")
                .encode(
                    x=alt.X("importance:Q", title="Feature importance"),
                    y=alt.Y("feature:N", sort="-x", title=None),
                    tooltip=[alt.Tooltip("feature:N", title="Feature"), alt.Tooltip("importance:Q", title="Importance", format=".4f")],
                )
                .properties(height=300)
            )
            st.altair_chart(feature_chart, width="stretch")
    st.markdown(
        '<div class="demo-note"><strong>Interpretation note:</strong> This is a portfolio demonstration evaluated on synthetic data. Better scores on this dataset do not guarantee the same performance on real retail data.</div>',
        unsafe_allow_html=True,
    )

st.divider()
st.caption("StockSense AI · Synthetic-data portfolio demo · Forecasts are decision-support estimates, not guaranteed business outcomes.")
