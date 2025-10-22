# ==========================================================
# 👨‍🏫 Faculty Workload Prediction Dashboard (Predicted Overload Risk + Department Charts)
# ==========================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from db import get_table

st.set_page_config(page_title="Faculty Workload Dashboard", layout="wide")
st.title("👨‍🏫 Faculty Workload & Predicted Overload Risk Dashboard")

# ----------------- Load Data -----------------
df = get_table("faculty")


# ----------------- Department-wise Charts in Columns with Hover Info -----------------
st.subheader("📊 Department-wise Faculty Analytics")

# Aggregate data per department
dept_agg = df.groupby('department').agg({
    'leaves_taken':'sum',
    'publications':'sum',
    'workshops_attended':'sum' if 'workshops_attended' in df.columns else 'sum',
    'awards_received':'sum' if 'awards_received' in df.columns else 'sum',
    'faculty_id':'count'  # total faculty per department
}).reset_index().rename(columns={'faculty_id':'faculty_count'})

# Create 4 columns
col1, col2= st.columns(2)

# Leaves Taken - Pie Chart with hover
if 'leaves_taken' in dept_agg.columns:
    fig_leaves = px.pie(
        dept_agg, 
        names='department', 
        values='leaves_taken',
        title="Leaves Taken by Department",
        hole=0.3,
        hover_data={'faculty_count': True, 'leaves_taken': True}
    )
    col1.plotly_chart(fig_leaves, use_container_width=True)

# Publications - Horizontal Bar Chart with hover
if 'publications' in dept_agg.columns:
    fig_pub = px.bar(
        dept_agg, 
        y='department', 
        x='publications', 
        color='department',
        orientation='h',
        title="Publications by Department",
        hover_data={'faculty_count': True, 'publications': True}
    )
    col2.plotly_chart(fig_pub, use_container_width=True)

col3, col4 = st.columns(2)
# Workshops Attended - Treemap with hover
if 'workshops_attended' in df.columns:
    fig_ws = px.treemap(
        dept_agg, 
        path=['department'], 
        values='workshops_attended',
        color='workshops_attended', 
        color_continuous_scale='Viridis',
        title="Workshops Attended by Department",
        hover_data={'faculty_count': True, 'workshops_attended': True}
    )
    col3.plotly_chart(fig_ws, use_container_width=True)

# Awards Received - Donut Chart with hover
if 'awards_received' in df.columns:
    fig_aw = px.pie(
        dept_agg, 
        names='department', 
        values='awards_received',
        title="Awards Received by Department",
        hole=0.5,
        hover_data={'faculty_count': True, 'awards_received': True}
    )
    col4.plotly_chart(fig_aw, use_container_width=True)

# ----------------- Workload Prediction -----------------
st.subheader("📈 Predicted Weekly Workload Hours for All Faculty")

# features = ['classes_handled_per_week','leaves_taken','research_projects','experience_years','publications','courses_taught']
features = ['classes_handled_per_week','leaves_taken','research_projects','experience_years','publications','courses_taught']
target = 'workload_hours'

X = df[features]
y = df[target]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train workload models (Regression)
@st.cache_resource
def train_workload_models(X_train, y_train, X_test, y_test):
    rf = RandomForestRegressor(n_estimators=150, random_state=42)
    rf.fit(X_train, y_train)
    rf_r2 = r2_score(y_test, rf.predict(X_test))
    
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_r2 = r2_score(y_test, lr.predict(X_test))
    
    best_model = rf if rf_r2 >= lr_r2 else lr
    best_r2 = max(rf_r2, lr_r2)
    mae = mean_absolute_error(y_test, best_model.predict(X_test))
    return best_model, best_r2, mae

workload_model, workload_r2, workload_mae = train_workload_models(X_train, y_train, X_test, y_test)
st.write(f"**Best Regression Model R²:** {workload_r2:.2f}, **MAE:** {workload_mae:.2f} %")

# Predict workload for all faculty
df['predicted_workload_hours'] = workload_model.predict(df[features])

# ----------------- Overload Risk Based on Predicted Workload -----------------
OVERLOAD_THRESHOLD = 30  # Adjust threshold if needed
df['predicted_overload_risk'] = (df['predicted_workload_hours'] > OVERLOAD_THRESHOLD).astype(int)

st.subheader("📊 Faculty Members at Risk (Based on Predicted Workload)")

overloaded_faculty = df[df['predicted_overload_risk'] == 1]

if not overloaded_faculty.empty:
    st.dataframe(overloaded_faculty[['faculty_id', 'department', 'predicted_workload_hours',
                                     'classes_handled_per_week', 'leaves_taken',
                                     'research_projects', 'experience_years','publications','courses_taught']])
    st.write(f"Total Faculty at Risk: **{len(overloaded_faculty)}**")
else:
    st.info("No faculty members are predicted to be above the overload threshold.")

# ----------------- Predicted Workload Scatter Plot -----------------
st.subheader("📊 Predicted Workload vs Classes Handled")

fig = px.scatter(
    df, 
    x="classes_handled_per_week", 
    y="predicted_workload_hours", 
    color="predicted_overload_risk",
    color_continuous_scale=['green','red'],
    hover_data=['faculty_id','experience_years','research_projects','leaves_taken','publications','courses_taught'],
    title="Predicted Workload Hours by Classes Handled (Hover for Details)",
    labels={"predicted_overload_risk":"Overload Risk"}
)

fig.add_hline(
    y=OVERLOAD_THRESHOLD, 
    line_dash="dash", 
    line_color="red", 
    annotation_text=f"Overload Threshold ({OVERLOAD_THRESHOLD}h)", 
    annotation_position="top left"
)

st.plotly_chart(fig, use_container_width=True)