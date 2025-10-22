# ==========================================================
# 🏢 Facility Analytics Dashboard (Month Slider + Forecast + Formatting)
# ==========================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import accuracy_score
from db import get_table

# ==========================================================
# ⚙️ PAGE SETUP
# ==========================================================
st.set_page_config(page_title="Facility Analytics Dashboard", layout="wide")
st.title("🏢 Facility Usage & Overcrowding Risk Dashboard")

# ==========================================================
# 📥 LOAD DATA
# ==========================================================
df = get_table("facility_logs")

# Ensure correct data types
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["month"] = df["date"].dt.to_period("M").astype(str)
df["check_in_time"] = pd.to_datetime(df["check_in_time"], format="%H:%M", errors="coerce")
df["check_out_time"] = pd.to_datetime(df["check_out_time"], format="%H:%M", errors="coerce")

# Keep a full copy for forecasting (unfiltered)
df_full = df.copy()

# ==========================================================
# 🚨 OVERCROWDING RISK CLASSIFICATION (on full data)
# ==========================================================
OVERCROWD_THRESHOLD = 1.5

if "crowding_index" in df_full.columns:
    df_full["overcrowded"] = (df_full["crowding_index"] > OVERCROWD_THRESHOLD).astype(int)

    # Predictive features
    features = ["is_weekend", "facility_capacity", "special_event", "temperature", "avg_duration_today"]
    X_features = [f for f in features if f in df_full.columns]
    y_cls = df_full["overcrowded"]

    if len(X_features) >= 1 and y_cls.nunique() > 1:
        X = df_full[X_features].fillna(0)
        X_train, X_test, y_train, y_test = train_test_split(X, y_cls, test_size=0.2, random_state=42)

        @st.cache_resource
        def train_overcrowding_model(X_train, y_train, X_test, y_test):
            clf = RandomForestClassifier(n_estimators=150, random_state=42)
            clf.fit(X_train, y_train)
            acc = accuracy_score(y_test, clf.predict(X_test))
            return clf, acc

        crowd_model, crowd_acc = train_overcrowding_model(X_train, y_train, X_test, y_test)
        st.success(f"✅ Overcrowding Model Accuracy: **{crowd_acc:.2f}**")

        df_full["predicted_overcrowding_risk"] = crowd_model.predict(X)
    else:
        st.warning("Insufficient variation in overcrowding data to train model.")
else:
    st.warning("Crowding index not found in dataset.")

# ==========================================================
# 🎚️ MONTH RANGE FILTER (for visuals only)
# ==========================================================
min_month = df["date"].min()
max_month = df["date"].max()

if min_month and max_month:
    st.sidebar.header("📆 Time Range Filter")
    start_date, end_date = st.sidebar.slider(
        "Select month range to visualize (forecast uses full history):",
        min_value=min_month.to_pydatetime(),
        max_value=max_month.to_pydatetime(),
        value=(min_month.to_pydatetime(), max_month.to_pydatetime()),
        format="MMM YYYY"
    )

    # Filter dashboard visuals
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # Map predicted overcrowding from full df to filtered df
    if "predicted_overcrowding_risk" in df_full.columns:
        df = df.merge(
            df_full[["date", "facility_name", "predicted_overcrowding_risk"]],
            on=["date", "facility_name"],
            how="left"
        )
else:
    st.warning("⚠️ No valid date data found.")

# ==========================================================
# 📊 DASHBOARD VISUALS
# ==========================================================
st.markdown("### 📊 Facility Insights (Filtered View)")

# --- KPI METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Logs", f"{len(df):,}")  # thousands separator
with col2:
    st.metric("Unique Facilities", f"{df['facility_name'].nunique():,}")
with col3:
    st.metric("Avg Feedback Rating", f"{df['feedback_rating'].mean():.2f}")

# ----------------- CHART 1: Monthly Usage -----------------
st.subheader("📈 Facility Usage Over Months")
usage_monthly = df.groupby(["month", "facility_name"])["duration_hr"].sum().reset_index()
fig1 = px.line(
    usage_monthly,
    x="month",
    y="duration_hr",
    color="facility_name",
    markers=True,
    title="Total Usage Hours per Facility Over the Month",
    labels={"duration_hr": "Total Usage Hours"}
)
st.plotly_chart(fig1, use_container_width=True)

# ----------------- CHART 2: User Type Analysis -----------------
if "user_type" in df.columns:
    st.subheader("👥 Usage Distribution by User Type")
    user_type_usage = df.groupby(["facility_name", "user_type"])["duration_hr"].sum().reset_index()
    fig2 = px.bar(
        user_type_usage,
        x="facility_name",
        y="duration_hr",
        color="user_type",
        barmode="group",
        title="Total Usage Hours by User Type",
        labels={"duration_hr": "Total Usage Hours"}
    )
    st.plotly_chart(fig2, use_container_width=True)

# ----------------- CHART 3: Zone-Based Usage -----------------
if "zone" in df.columns:
    st.subheader("🏗️ Indoor vs Outdoor Facility Usage")
    zone_usage = df.groupby(["zone", "facility_name"])["duration_hr"].sum().reset_index()
    fig3 = px.bar(
        zone_usage,
        x="facility_name",
        y="duration_hr",
        color="zone",
        barmode="group",
        title="Indoor vs Outdoor Facility Usage",
        labels={"duration_hr": "Total Usage Hours"}
    )
    st.plotly_chart(fig3, use_container_width=True)

# ----------------- CHART 4: Feedback vs Crowding -----------------
st.subheader("⭐ Average Feedback vs Crowding Index")
feedback_vs_crowd = df.groupby("facility_name")[["feedback_rating", "crowding_index"]].mean().reset_index()
feedback_vs_crowd["feedback_rating"] = feedback_vs_crowd["feedback_rating"].round(2)
feedback_vs_crowd["crowding_index"] = feedback_vs_crowd["crowding_index"].round(2)
fig4 = px.scatter(
    feedback_vs_crowd,
    x="crowding_index",
    y="feedback_rating",
    color="facility_name",
    size="crowding_index",
    title="Feedback Rating vs Crowding Index (avg per facility)",
    labels={"crowding_index": "Crowding Index", "feedback_rating": "Feedback Rating"}
)
st.plotly_chart(fig4, use_container_width=True)

# ----------------- CHART 5: Overcrowding Risk Over the Month -----------------
if "predicted_overcrowding_risk" in df.columns:
    st.subheader("🚨 Predicted Overcrowding Risk Over the Month (Filtered View)")
    df["predicted_overcrowding_risk_pct"] = df["predicted_overcrowding_risk"] * 100
    overcrowd_monthly = df.groupby(["month", "facility_name"])["predicted_overcrowding_risk_pct"].sum().reset_index()
    fig5 = px.line(
        overcrowd_monthly,
        x="month",
        y="predicted_overcrowding_risk_pct",
        color="facility_name",
        markers=True,
        title="Predicted Overcrowding Risk per Facility Over the Month",
        labels={"predicted_overcrowding_risk_pct": "Overcrowding Risk (%)"}
    )
    st.plotly_chart(fig5, use_container_width=True)

# ==========================================================
# 🔮 FORECAST (full history)
# ==========================================================
st.markdown("### 🔮 Overcrowding Forecast (Next 6 Months — Full History)")

if "overcrowded" in df_full.columns:
    overcrowd_hist = (
        df_full.groupby([df_full["date"].dt.to_period("M"), "facility_name"])["overcrowded"]
        .mean()
        .reset_index()
        .rename(columns={"overcrowded": "avg_risk"})
    )
    overcrowd_hist["month"] = overcrowd_hist["date"].astype(str)
    overcrowd_hist["month_idx"] = overcrowd_hist.groupby("facility_name").cumcount()

    forecast_all = []

    for facility in overcrowd_hist["facility_name"].unique():
        sub_df = overcrowd_hist[overcrowd_hist["facility_name"] == facility]
        if len(sub_df) < 3:
            continue

        X = sub_df[["month_idx"]]
        y = sub_df["avg_risk"]

        # Multiple models
        lr = LinearRegression()
        rf = RandomForestRegressor(n_estimators=150, random_state=42)
        knn = KNeighborsRegressor(n_neighbors=min(3, len(sub_df) - 1))

        lr.fit(X, y)
        rf.fit(X, y)
        knn.fit(X, y)

        # Forecast next 6 months
        future_idx = np.arange(len(sub_df), len(sub_df) + 6).reshape(-1, 1)
        preds_lr = lr.predict(future_idx)
        preds_rf = rf.predict(future_idx)
        preds_knn = knn.predict(future_idx)

        # Ensemble average
        ensemble_pred = (preds_lr + preds_rf + preds_knn) / 3
        ensemble_pred = np.clip(ensemble_pred, 0, 1)

        last_period = pd.Period(sub_df["date"].iloc[-1], freq="M")
        future_months = pd.period_range(start=last_period + 1, periods=6, freq="M").astype(str)

        temp_df = pd.DataFrame({
            "facility_name": facility,
            "month": future_months,
            "predicted_avg_risk": ensemble_pred
        })
        temp_df["predicted_avg_risk_pct"] = temp_df["predicted_avg_risk"] * 100
        forecast_all.append(temp_df)

    if forecast_all:
        forecast_df = pd.concat(forecast_all, ignore_index=True)
        fig_forecast = px.line(
            forecast_df,
            x="month",
            y="predicted_avg_risk_pct",
            color="facility_name",
            markers=True,
            title="Overcrowding Forecast by Facility (Next 6 Months)",
            labels={"predicted_avg_risk_pct": "Forecasted Risk (%)"}
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.warning("⚠️ Not enough data to forecast for any facility.")
else:
    st.warning("⚠️ Overcrowding data unavailable — cannot generate forecast.")
