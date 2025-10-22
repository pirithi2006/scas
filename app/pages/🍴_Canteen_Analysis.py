# ==========================================================
# 🍴 Canteen Analytics Dashboard (Forecasting, Revenue, Event Impact)
# Enhanced: time-slot charts, weather & footfall analysis, 90-day forecast & CSV export
# ==========================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from db import get_table
import io

# ==========================================================
# PAGE SETUP
# ==========================================================
st.set_page_config(page_title="Canteen Analytics Dashboard", layout="wide")
st.title("🍴 Canteen Demand & Revenue Analysis ")

# ==========================================================
# LOAD DATA
# ==========================================================
df = get_table("canteen")  # expects price_inr = total revenue, qty_sold etc.

# Basic cleaning / derived columns
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.sort_values(['item','date']).reset_index(drop=True)
df['month'] = df['date'].dt.to_period('M').astype(str)
# derive unit_price (should be stable if price_inr = base_price * qty)
df['unit_price'] = (df['price_inr'] / df['qty_sold']).replace([np.inf, -np.inf], np.nan).fillna(0)

# Ensure optional fields present (added earlier)
for col in ['time_slot','time_slot_code','footfall','weather_condition','previous_day_qty']:
    if col not in df.columns:
        if col == 'time_slot_code':
            df[col] = 0
        elif col == 'time_slot':
            df[col] = 'All'
        elif col == 'footfall':
            df[col] = 600
        elif col == 'weather_condition':
            df[col] = 'Sunny'
        else:
            df[col] = 0

# Keep full copy for forecasting (visual filter must not affect models)
df_full = df.copy()

# ==========================================================
# SIDEBAR: month filter (visuals only) & forecast horizon
# ==========================================================
min_date = df['date'].min()
max_date = df['date'].max()

st.sidebar.header("Filters & Forecast Settings")
if pd.notnull(min_date) and pd.notnull(max_date):
    start_date, end_date = st.sidebar.slider(
        "Select date range (visuals only):",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
        format="MMM YYYY"
    )
else:
    start_date, end_date = min_date, max_date

df_vis = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

forecast_days = st.sidebar.slider("Forecast horizon (days)", min_value=7, max_value=90, value=30, step=1)
# quick button preset for 90-day (3 months)
if st.sidebar.button("Set 90-day forecast"):
    forecast_days = 90

# ==========================================================
# DASHBOARD KPIs (filtered view)
# ==========================================================
st.subheader("📊 Key Metrics (Filtered View)")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Records", f"{len(df_vis):,}")
with col2:
    st.metric("Unique Items", df_vis['item'].nunique())
with col3:
    st.metric("Avg Unit Price (INR)", f"{df_vis['unit_price'].mean():.2f}")
with col4:
    st.metric("Avg Qty Sold", f"{df_vis['qty_sold'].mean():.1f}")

# ==========================================================
# VISUALS (filtered)
# ==========================================================
st.subheader("📈 Demand & Revenue Visuals")

# Total daily demand
daily_demand = df_vis.groupby('date').agg(
    total_qty=('qty_sold','sum'),
    total_revenue=('price_inr','sum')
).reset_index()

fig_daily = px.line(daily_demand, x='date', y=['total_qty','total_revenue'],
                    title="Total Daily Quantity & Revenue",
                    labels={'value': 'Value', 'date':'Date', 'variable':'Metric'})
st.plotly_chart(fig_daily, use_container_width=True)

# Item demand by category
item_cat = df_vis.groupby(['item','category']).agg(total_qty=('qty_sold','sum'), total_revenue=('price_inr','sum')).reset_index()
fig_item = px.bar(item_cat, x='item', y='total_qty', color='category', title="Total Quantity Sold per Item (by Category)", labels={'total_qty':'Total Qty'})
st.plotly_chart(fig_item, use_container_width=True)

# Category trend
cat_trend = df_vis.groupby(['date','category'])['qty_sold'].sum().reset_index()
fig_cat = px.line(cat_trend, x='date', y='qty_sold', color='category', title="Daily Quantity per Category")
st.plotly_chart(fig_cat, use_container_width=True)

# ==========================================================
# NEW: Time-slot breakdown
# ==========================================================
st.subheader("⏰ Time-slot Demand Breakdown")
ts = df_vis.groupby(['time_slot','item']).qty_sold.sum().reset_index()
fig_ts = px.bar(ts, x='time_slot', y='qty_sold', color='item', title="Quantity by Time Slot and Item", barmode='stack')
st.plotly_chart(fig_ts, use_container_width=True)

# ==========================================================
# NEW: Weather impact & Footfall analysis
# ==========================================================
st.subheader("🌦️ Weather & Footfall Impact")

# ==========================================================
# 🌦 Weather Condition Impact — Average Quantity by Item
# ==========================================================
# Aggregate by weather_condition and item
weather_item_agg = df_full.groupby(['weather_condition','item']).agg(
    avg_qty=('qty_sold','mean'),
    total_qty=('qty_sold','sum'),
    count=('qty_sold','count')
).reset_index()

# Plot: avg quantity by weather condition, colored by item
fig_weather = px.bar(
    weather_item_agg,
    x='weather_condition',
    y='avg_qty',
    color='item',
    title='🌦 Average Quantity by Weather Condition (per Item)',
    labels={'avg_qty':'Avg Qty', 'weather_condition':'Weather Condition'}
)

fig_weather.update_traces(textposition='outside')  # show item names on bars
st.plotly_chart(fig_weather, use_container_width=True)

# ==========================================================
# Footfall vs Total Daily Quantity (Enhanced)
# ==========================================================
# Aggregate daily footfall and total qty
footfall_df = df_full.groupby('date').agg(
    footfall=('footfall', 'mean'),
    total_qty=('qty_sold', 'sum'),
    special_event=('special_event', 'first'),
    weekday=('weekday', 'first')
).reset_index()

# Correlation coefficient
corr = footfall_df['footfall'].corr(footfall_df['total_qty'])

# Scatter plot with color by special_event and hover info
fig_scatter = px.scatter(
    footfall_df,
    x='footfall',
    y='total_qty',
    color='special_event',          # color points by events
    hover_data={
        'date': True,
        'footfall': True,
        'total_qty': True,
        'weekday': True
    },
    trendline='ols',
    title=f'Footfall vs Daily Total Quantity (corr={corr:.2f})'
)

fig_scatter.update_layout(
    legend_title_text='Event Type',
    xaxis_title='Footfall (No. of Visitors)',
    yaxis_title='Total Quantity Sold'
)

st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================================
# EVENT / HOLIDAY IMPACT ANALYSIS (uses full history)
# ==========================================================
st.subheader("🎉 Event & Holiday Impact")
col1, col2 = st.columns(2)

# --- Clean and normalize the special_event column ---
df_full['special_event'] = (
    df_full['special_event']
    .astype(str)                     # ensure it's string
    .str.strip()                     # remove spaces
    .replace(['', 'nan', 'None', 'NONE', 'none', 'NaN', 'Null', 'null'], 'None')
    .fillna('None')
)

# --- Overall uplift during special events vs baseline ---
baseline = (
    df_full[df_full['special_event'] == 'None']
    .groupby('item')['qty_sold']
    .mean()
    .rename('baseline_mean')
)

event_means = (
    df_full[df_full['special_event'] != 'None']
    .groupby('item')['qty_sold']
    .mean()
    .rename('event_mean')
)

impact_df = pd.concat([baseline, event_means], axis=1).fillna(0).reset_index()

impact_df['event_uplift_pct'] = np.where(
    impact_df['baseline_mean'] > 0,
    (impact_df['event_mean'] - impact_df['baseline_mean']) / impact_df['baseline_mean'] * 100,
    np.nan
)

with col1:
    st.write("Average uplift (quantity) during any special event vs baseline (by item):")
    st.dataframe(
        impact_df[['item', 'baseline_mean', 'event_mean', 'event_uplift_pct']]
        .style.format({
            'baseline_mean': '{:.1f}',
            'event_mean': '{:.1f}',
            'event_uplift_pct': '{:+.1f}%'
        })
    )

# ==========================================================
# HOLIDAY / WEEKEND IMPACT
# ==========================================================
holiday_baseline = (
    df_full[df_full['holiday_flag'] == 0]
    .groupby('item')['qty_sold']
    .mean()
    .rename('weekday_mean')
)
holiday_mean = (
    df_full[df_full['holiday_flag'] == 1]
    .groupby('item')['qty_sold']
    .mean()
    .rename('holiday_mean')
)

holiday_df = pd.concat([holiday_baseline, holiday_mean], axis=1).fillna(0).reset_index()
holiday_df['holiday_uplift_pct'] = np.where(
    holiday_df['weekday_mean'] > 0,
    (holiday_df['holiday_mean'] - holiday_df['weekday_mean']) / holiday_df['weekday_mean'] * 100,
    np.nan
)

with col2:
    st.write("Average change (quantity) on holidays/weekends vs weekdays (by item):")
    st.dataframe(
        holiday_df[['item', 'weekday_mean', 'holiday_mean', 'holiday_uplift_pct']]
        .style.format({
            'weekday_mean': '{:.1f}',
            'holiday_mean': '{:.1f}',
            'holiday_uplift_pct': '{:+.1f}%'
        })
    )

# ==========================================================
# 🔮 Forecast Next N Days per Item — Realistic Forecast
# ==========================================================
st.subheader(f"🔮 Forecast Next {forecast_days} Days per Item — Quantity, Revenue & Footfall")

from sklearn.preprocessing import OneHotEncoder

forecast_all = []
items = df_full['item'].unique()
median_prices = df_full.groupby('item')['unit_price'].median().to_dict()

# -----------------------------
# Footfall model based on historical weekday, holiday, and special_event
# -----------------------------
footfall_hist = df_full.groupby('date').agg(
    footfall=('footfall','mean'),
    weekday=('weekday','first'),
    holiday_flag=('holiday_flag','first'),
    special_event=('special_event','first')
).reset_index()

X_footfall = pd.get_dummies(footfall_hist[['weekday','holiday_flag','special_event']], drop_first=True)
y_footfall = footfall_hist['footfall']
footfall_model = LinearRegression()
footfall_model.fit(X_footfall, y_footfall)

# -----------------------------
# Future dates
# -----------------------------
last_date = df_full['date'].max()
future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=forecast_days)

# Simulate future events probabilistically
events = ['None','Sports Day','Cultural Fest','Tech Meet']
probs = [0.8, 0.07, 0.08, 0.05]
future_events = np.random.choice(events, size=forecast_days, p=probs)
future_weekdays = future_dates.weekday
future_holidays = [1 if d>=5 else 0 for d in future_weekdays]

future_df_base = pd.DataFrame({
    'date': future_dates,
    'weekday': future_weekdays,
    'holiday_flag': future_holidays,
    'special_event': future_events
})

# -----------------------------
# Forecast per item
# -----------------------------
for item in items:
    item_hist = df_full[df_full['item']==item].groupby('date').agg(
        qty=('qty_sold','sum'),
        footfall=('footfall','mean'),
        weekday=('weekday','first'),        # same for all rows of a date
        holiday_flag=('holiday_flag','first'),
        special_event=('special_event', lambda x: ','.join(sorted(x.unique()))),
        promotion_flag=('promotion_flag','max'),
        time_slot_code=('time_slot_code','max'),
        previous_day_qty=('previous_day_qty','sum')
    ).reset_index().sort_values('date')

    if len(item_hist) < 3:
        continue

    # -----------------------------
    # Train ensemble models on historical features
    # -----------------------------
    X_hist = pd.get_dummies(item_hist[['weekday','holiday_flag','special_event']], drop_first=True)
    y_hist = item_hist['qty']

    m1 = LinearRegression(); m1.fit(X_hist, y_hist)
    m2 = RandomForestRegressor(n_estimators=200, random_state=42); m2.fit(X_hist, y_hist)
    m3 = GradientBoostingRegressor(n_estimators=200, random_state=42); m3.fit(X_hist, y_hist)

    # -----------------------------
    # Prepare future features
    # -----------------------------
    X_future = pd.get_dummies(future_df_base[['weekday','holiday_flag','special_event']], drop_first=True)
    for col in X_hist.columns:
        if col not in X_future.columns:
            X_future[col] = 0
    X_future = X_future[X_hist.columns]

    # -----------------------------
    # Forecast quantity
    # -----------------------------
    p1 = m1.predict(X_future)
    p2 = m2.predict(X_future)
    p3 = m3.predict(X_future)
    ensemble_qty = np.clip((p1 + p2 + p3)/3, 0, None)

    # -----------------------------
    # Forecast footfall
    # -----------------------------
    future_df_ff = X_future.copy()
    future_df_ff['weekday'] = future_df_base['weekday']
    future_df_ff['holiday_flag'] = future_df_base['holiday_flag']
    # Some columns may be missing if dropped in dummies
    X_future_ff = pd.get_dummies(future_df_base[['weekday','holiday_flag','special_event']], drop_first=True)
    for col in X_footfall.columns:
        if col not in X_future_ff.columns:
            X_future_ff[col] = 0
    X_future_ff = X_future_ff[X_footfall.columns]
    forecast_footfall = footfall_model.predict(X_future_ff)

    # -----------------------------
    # Forecast revenue
    # -----------------------------
    unit_price = median_prices.get(item, df_full['unit_price'].median())

    future_item_df = future_df_base.copy()
    future_item_df['item'] = item
    future_item_df['forecast_qty'] = ensemble_qty
    future_item_df['forecast_revenue'] = ensemble_qty * unit_price
    future_item_df['forecast_footfall'] = forecast_footfall

    forecast_all.append(future_item_df[['date','item','forecast_qty','forecast_revenue','forecast_footfall']])

# -----------------------------
# Combine all items and plot
# -----------------------------
if forecast_all:
    forecast_df = pd.concat(forecast_all, ignore_index=True)

    # Forecast Quantity
    fig_qty = px.line(forecast_df, x='date', y='forecast_qty', color='item',
                      title="Forecasted Quantity Sold per Item")
    st.plotly_chart(fig_qty, use_container_width=True)

    # Forecast Revenue
    fig_rev = px.line(forecast_df, x='date', y='forecast_revenue', color='item',
                      title="Forecasted Revenue per Item")
    st.plotly_chart(fig_rev, use_container_width=True)

    # Forecast Footfall (aggregated)
    footfall_agg = forecast_df.groupby('date')['forecast_footfall'].sum().reset_index()
    fig_footfall = px.line(footfall_agg, x='date', y='forecast_footfall',
                           title="Forecasted Total Footfall")
    st.plotly_chart(fig_footfall, use_container_width=True)

    # Top 10 items by forecast revenue
    rev_by_item = forecast_df.groupby('item')['forecast_revenue'].sum().reset_index().sort_values('forecast_revenue', ascending=False)
    st.write("Top items by forecasted revenue:")
    st.dataframe(rev_by_item.head(10).style.format({'forecast_revenue':'{:.0f}'}))

else:
    st.info("Not enough historical data per item to forecast.")
