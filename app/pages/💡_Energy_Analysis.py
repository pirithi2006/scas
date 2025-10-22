# ==========================================================
# 💡 Energy Analytics Page
# ==========================================================
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_percentage_error
from db import get_table
import plotly.figure_factory as ff

st.title("💡 Energy Consumption Analysis & Model Comparison")

# -------------------------------
# Load energy dataset
# -------------------------------
df = get_table("energy")
df['date'] = pd.to_datetime(df['date'])
df['week_num'] = df['date'].dt.isocalendar().week

# -------------------------------
# Initialize session state
# -------------------------------
if 'st.session_state.selected_week' not in st.session_state:
    st.session_state.selected_week = (int(df['week_num'].min()), int(df['week_num'].max()))

if 'st.session_state.selected_buildings' not in st.session_state:
    st.session_state.selected_buildings = df['building'].unique().tolist()

if 'future_df' not in st.session_state:
    st.session_state.future_df = pd.DataFrame()

if 'fig_daily' not in st.session_state:
    st.session_state.fig_daily = None

if 'fig_ma' not in st.session_state:
    st.session_state.fig_ma = None

if 'fig_pred' not in st.session_state:
    st.session_state.fig_pred = None

if 'forecast_weeks' not in st.session_state:
    st.session_state.forecast_weeks = 2

if 'forecast_start' not in st.session_state:
    st.session_state.forecast_start = df['date'].max()
    
# -------------------------------
# Overview
# -------------------------------
st.subheader("📊 Overview")
st.dataframe(df.head())

# -------------------------------
# Week Selection
# -------------------------------
st.subheader("📅 Select Week(s) - Need at least 2 Weeks for prediction")
min_week, max_week = int(df['week_num'].min()), int(df['week_num'].max())
st.session_state.selected_week = st.slider("Week Number", min_value=min_week, max_value=max_week, value=st.session_state.selected_week)
df_filtered = df[(df['week_num'] >= st.session_state.selected_week[0]) & (df['week_num'] <= st.session_state.selected_week[1])]

# -------------------------------
# Building Selection with Select All
# -------------------------------
st.subheader("🏢 Select Buildings")
buildings = df_filtered['building'].unique().tolist()
st.session_state.selected_buildings = st.multiselect(
    "Buildings", 
    options=buildings, 
    default=buildings
)
if not st.session_state.selected_buildings:
    st.session_state.selected_buildings = buildings  # Ensure at least all are selected

df_filtered = df_filtered[df_filtered['building'].isin(st.session_state.selected_buildings)]

# -------------------------------
# Energy Consumption Over Time
# -------------------------------
st.subheader("📈 Energy Consumption Over Time")
df_daily = df_filtered.groupby(['date', 'building'])['energy_kwh'].mean().reset_index()
df_daily['energy_ma7'] = df_daily.groupby('building')['energy_kwh'].transform(lambda x: x.rolling(7, 1).mean())

fig_raw = px.line(df_daily, x='date', y='energy_kwh', color='building',
                  title=f"Daily Energy Consumption (Week {st.session_state.selected_week[0]} to {st.session_state.selected_week[1]})",
                  labels={'energy_kwh': 'Energy (kWh)'})
st.plotly_chart(fig_raw, use_container_width=True)

fig_ma = px.line(df_daily, x='date', y='energy_ma7', color='building',
                 title=f"7-Day Moving Average Energy Consumption (Week {st.session_state.selected_week[0]} to {st.session_state.selected_week[1]})",
                 labels={'energy_ma7': 'Energy (kWh)'})
st.plotly_chart(fig_ma, use_container_width=True)

# -------------------------------
# Weekly aggregation and features
# -------------------------------
all_features = ['temp_c','humidity_pct','occupancy_estimate','weekday','holiday_flag',
                'outside_temp_c','rainfall_mm','building_area_sqm','floor_count',
                'equipment_factor','class_event_count']
features = [f for f in all_features if f in df_filtered.columns]

df_filtered['week_start'] = df_filtered['date'] - pd.to_timedelta(df_filtered['date'].dt.weekday, unit='d')
agg_dict = {f:'mean' for f in features if f in df_filtered.columns}
agg_dict['energy_kwh'] = 'mean'
df_weekly = df_filtered.groupby(['week_start','building']).agg(agg_dict).reset_index()

# Lag features
for lag in [1,2]:
    df_weekly[f'lag_{lag}'] = df_weekly.groupby('building')['energy_kwh'].shift(lag)

# Fill NaN values
df_weekly = df_weekly.ffill().bfill()
ml_features = features + [f'lag_{i}' for i in [1,2]]


# ------------------------------- # Top 5 Buildings by Average Energy Consumption # ------------------------------- 
st.subheader("🏢 Top 5 Buildings by Average Energy Consumption") 
top_buildings = df_filtered.groupby("building")["energy_kwh"].mean().sort_values(ascending=False).head(5).reset_index() 
fig_top_buildings = px.bar( top_buildings, x="building", y="energy_kwh", text="energy_kwh", title="Top 5 Buildings by Average Energy Consumption", labels={"energy_kwh": "Avg Energy (kWh)", "building": "Building"}, color="energy_kwh", color_continuous_scale="Viridis" ) 
fig_top_buildings.update_traces(texttemplate="%{text:.2f}", textposition="outside") 
fig_top_buildings.update_layout(yaxis=dict(title="Average Energy (kWh)"), xaxis=dict(title="Building")) 
st.plotly_chart(fig_top_buildings, use_container_width=True)


# ==========================================================
# ⚡ Energy Efficiency Analysis (Based on Area & Floors)
# ==========================================================
st.subheader("⚙️ Energy Efficiency Analysis")

# Ensure required columns exist
if all(col in df_filtered.columns for col in ["building_area_sqm", "floor_count"]):
    # Compute efficiency metrics
    df_eff = df_filtered.groupby("building").agg({
        "energy_kwh": "mean",
        "building_area_sqm": "mean",
        "floor_count": "mean"
    }).reset_index()

    # Energy efficiency = energy consumption per sqm per floor
    df_eff["energy_per_sqm_floor"] = df_eff["energy_kwh"] / (df_eff["building_area_sqm"] * df_eff["floor_count"])
    df_eff = df_eff.sort_values(by="energy_per_sqm_floor", ascending=False)

    # Visualization 1: Bar Chart (Efficiency Ranking)
    fig_eff = px.bar(
        df_eff,
        x="building",
        y="energy_per_sqm_floor",
        color="energy_per_sqm_floor",
        color_continuous_scale="RdYlGn_r",
        text="energy_per_sqm_floor",
        title="Energy Efficiency by Building (kWh per sqm per floor) - lower is better",
        labels={"energy_per_sqm_floor": "Energy / sqm / floor"}
    )
    fig_eff.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig_eff.update_layout(
        xaxis_title="Building",
        yaxis_title="Energy per sqm per floor",
        yaxis=dict(showgrid=True),
        xaxis=dict(showticklabels=True)
    )
    st.plotly_chart(fig_eff, use_container_width=True)

st.subheader("🤖 Predict Energy Usage & Compare Models")

# -------------------------------
# Model Comparison with Dynamic KNN
# -------------------------------
X = df_weekly[ml_features].values
y = df_weekly['energy_kwh'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Adjust n_neighbors for KNN
n_neighbors = min(5, len(X_train))
models = {
    "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
    "Linear Regression": LinearRegression(),
    "KNN Regressor": KNeighborsRegressor(n_neighbors=n_neighbors),
    "SVR": SVR(kernel='rbf', C=100, gamma=0.1, epsilon=0.1)
}

results = []
for name, model in models.items():
    if len(X_train) < 1:  # Skip models if no training data
        continue
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred) * 100
    results.append({"Model": name, "R2": r2, "MAPE": mape, "FittedModel": model})

results_df = pd.DataFrame(results)
best_model_row = results_df.loc[results_df["MAPE"].idxmin()]
best_model_name = best_model_row["Model"]
best_model = best_model_row["FittedModel"]

# -------------------------------
# Show model comparison
# -------------------------------
st.write("📊 Model Comparison")
st.dataframe(results_df[['Model','R2','MAPE']].sort_values(by='MAPE'))
st.markdown(f"### ✅ Recommended Model: **{best_model_name}** (Lowest MAPE)")

# -------------------------------
# Forecast Future Weeks
# -------------------------------
num_future_weeks = st.slider("🔮 Forecast Weeks Ahead", 1, 8, 2)
last_week = df_weekly['week_start'].max()
future_data = []

for i in range(1, num_future_weeks + 1):
    for b in df_weekly['building'].unique():
        row = df_weekly[df_weekly['building'] == b].iloc[-1].copy()
        row['week_start'] = last_week + pd.Timedelta(weeks=i)
        X_row = row[ml_features].values.reshape(1, -1)
        base_pred = best_model.predict(X_row)[0]
        noise = np.random.normal(0, base_pred * 0.05)
        trend_adj = i * 0.02 * base_pred
        row['energy_pred'] = base_pred + trend_adj + noise
        future_data.append(row)

future_df = pd.DataFrame(future_data)

# Combine Actual + Predicted
last_actuals = df_weekly.groupby("building")[["week_start", "energy_kwh"]].last().reset_index()
last_actuals = last_actuals.rename(columns={"energy_kwh": "Actual"})
first_preds = future_df.groupby("building")[["week_start", "energy_pred"]].first().reset_index()
first_preds = first_preds.rename(columns={"energy_pred": "Predicted"})

bridge_rows = []
for _, row in last_actuals.iterrows():
    b = row["building"]
    first_pred = first_preds[first_preds["building"] == b]
    if not first_pred.empty:
        bridge_rows.append({
            "week_start": row["week_start"],
            "building": b,
            "Type": "Predicted",
            "Energy_KWh": row["Actual"]
        })

df_plot_actual = df_weekly[['week_start', 'building', 'energy_kwh']].rename(columns={'energy_kwh': 'Energy_KWh'})
df_plot_actual["Type"] = "Actual"
df_plot_pred = future_df[['week_start', 'building', 'energy_pred']].rename(columns={'energy_pred': 'Energy_KWh'})
df_plot_pred["Type"] = "Predicted"
df_plot_bridge = pd.DataFrame(bridge_rows)
df_plot_final = pd.concat([df_plot_actual, df_plot_bridge, df_plot_pred], ignore_index=True)

# -------------------------------
# Plot Actual vs Predicted (with gray forecast area)
# -------------------------------
forecast_start = pd.to_datetime(df_weekly['week_start'].max())
fig_pred = px.line(
    df_plot_final,
    x="week_start",
    y="Energy_KWh",
    color="building",
    line_dash="Type",
    labels={"week_start": "Week Start", "Energy_KWh": "Energy (kWh)", "Type": "Actual / Predicted"},
    title=f"Weekly Energy: Actual vs Predicted ({num_future_weeks}-Week Forecast)"
)

# Gray forecast area
fig_pred.add_vrect(
    x0=forecast_start,
    x1=df_plot_final["week_start"].max(),
    fillcolor="gray",
    opacity=0.2,
    layer="below",
    line_width=0
)

st.plotly_chart(fig_pred, use_container_width=True)