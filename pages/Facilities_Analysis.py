import pandas as pd
import streamlit as st
import sqlite3
import plotly.express as px

# -----------------------------
# Helper Functions
# -----------------------------
def sdiv(a, b, default=0.0):
    return (a / b) if b else default

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

# -----------------------------
# DB Config
# -----------------------------
DB_PATH = "datascas.db"
TABLE_NAME = "Facilities"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
conn.commit()

# -----------------------------
# Load Data
# -----------------------------
df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)

st.set_page_config(page_title="SCAS - Facilities Analysis", layout="wide")
st.title("🏢 Facilities Analysis")

# -----------------------------
# Data Validation
# -----------------------------
error_messages = []
if (df["AverageDailyUsers"] > df["Capacity"]).any():
    bad_ids = df.loc[df["AverageDailyUsers"] > df["Capacity"], "FacilityID"].tolist()
    error_messages.append(f"⚠️ Some facilities exceed capacity! IDs: {bad_ids}")

if (df["UsageHoursPerDay"] < 0).any():
    bad_ids = df.loc[df["UsageHoursPerDay"] < 0, "FacilityID"].tolist()
    error_messages.append(f"⚠️ Negative usage hours detected! IDs: {bad_ids}")

if (df["Capacity"] <= 0).any():
    bad_ids = df.loc[df["Capacity"] <= 0, "FacilityID"].tolist()
    error_messages.append(f"⚠️ Some facilities have zero/negative capacity! IDs: {bad_ids}")

if error_messages:
    st.warning("### 🚨 Data Validation Issues Found:")
    for msg in error_messages:
        st.write(msg)
else:
    st.success("✅ No major data issues found.")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters - Facilities")
all_types = sorted(df["FacilityType"].dropna().unique())
sel_types = st.sidebar.multiselect("Facility Type(s)", all_types)

all_status = sorted(df["MaintenanceStatus"].dropna().unique())
sel_status = st.sidebar.multiselect("Maintenance Status", all_status)

df_f = df.copy()
if sel_types:
    df_f = df_f[df_f["FacilityType"].isin(sel_types)]
if sel_status:
    df_f = df_f[df_f["MaintenanceStatus"].isin(sel_status)]

# -----------------------------
# KPIs
# -----------------------------
n = len(df_f)
avg_daily_users = round(df_f["AverageDailyUsers"].mean(), 2) if n else 0
avg_util = round((df_f["AverageDailyUsers"] / df_f["Capacity"] * 100).mean(), 2) if n else 0
avg_usage_hours = round(df_f["UsageHoursPerDay"].mean(), 2) if n else 0
needs_repair_pct = round(sdiv((df_f["MaintenanceStatus"] == "Needs Repair").sum(), n, 0) * 100, 2) if n else 0
under_maint_count = int((df_f["MaintenanceStatus"] == "Under Maintenance").sum()) if n else 0
most_freq_type = df_f["FacilityType"].value_counts().idxmax() if n else "—"

hi_used_label, hi_used_val = "—", 0
if n:
    hi_row = df_f.loc[df_f["AverageDailyUsers"].idxmax()]
    hi_used_label = f'{hi_row["FacilityType"]} ({hi_row["FacilityID"]})'
    hi_used_val = int(hi_row["AverageDailyUsers"])

# KPI Layout
st.subheader("🎯 KPIs")
c1, c2, c3 = st.columns(3)
c1.metric("Total Facilities", n)
c1.metric("Avg Daily Users", avg_daily_users)
c1.metric("Avg Capacity Utilization %", avg_util)

c2.metric("Avg Usage Hours/Day", avg_usage_hours)
c2.metric("Facilities Needing Repair %", needs_repair_pct)
c2.metric("Under Maintenance (Count)", under_maint_count)

c3.metric("Most Frequent Facility Type", most_freq_type)
c3.metric("Highest Used Facility", f"{hi_used_label}")

# -----------------------------
# Charts
# -----------------------------
st.markdown("---")
st.subheader("📈 Visualizations")
colA, colB = st.columns(2)
if n:
    fig1 = px.pie(df_f, names="FacilityType", title="Facilities by Type")
    colA.plotly_chart(fig1, use_container_width=True)
    fig2 = px.pie(df_f, names="MaintenanceStatus", title="Maintenance Status Distribution")
    colB.plotly_chart(fig2, use_container_width=True)

colC, colD = st.columns(2)
if n:
    fig3 = px.bar(df_f, x="FacilityType", y="UsageHoursPerDay", title="Usage Hours per Day by Facility Type")
    colC.plotly_chart(fig3, use_container_width=True)
    util_df = df_f.assign(Utilization=(df_f["AverageDailyUsers"] / df_f["Capacity"] * 100))
    fig4 = px.box(util_df, x="FacilityType", y="Utilization", title="Utilization % by Facility Type")
    colD.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# CRUD: Add / Edit Facility
# -----------------------------
st.markdown("---")
st.subheader("✏️ Add / Edit Facility")

facility_ids = ["—"] + df_f["FacilityID"].tolist()
sel_facility = st.selectbox("Select Facility to Edit", facility_ids)

if sel_facility != "—":
    fac_data = df[df["FacilityID"] == sel_facility].iloc[0].to_dict()
else:
    fac_data = {col: "" for col in df.columns}

col1, col2, col3, col4 = st.columns(4)
facility_type = col1.text_input("Facility Type", fac_data.get("FacilityType", ""))
capacity = col2.number_input("Capacity", min_value=0, value=safe_int(fac_data.get("Capacity"), 0))
avg_daily_users = col3.number_input("Average Daily Users", min_value=0, value=safe_int(fac_data.get("AverageDailyUsers"), 0))
usage_hours = col4.number_input("Usage Hours/Day", min_value=0.0, value=safe_float(fac_data.get("UsageHoursPerDay"), 0.0))

col5, col6 = st.columns(2)
status_options = ["Good", "Under Maintenance", "Needs Repair"]
default_status = fac_data.get("MaintenanceStatus", "Good")
if default_status not in status_options:
    default_status = "Good"

maintenance_status = col5.selectbox(
    "Maintenance Status",
    status_options,
    index=status_options.index(default_status)
)
location = col6.text_input("Location", fac_data.get("Location", ""))

if st.button("💾 Save Facility"):
    data_dict = {
        "FacilityID": sel_facility if sel_facility != "—" else f"FAC{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
        "FacilityType": facility_type,
        "Capacity": capacity,
        "AverageDailyUsers": avg_daily_users,
        "UsageHoursPerDay": usage_hours,
        "MaintenanceStatus": maintenance_status,
    }

    if sel_facility == "—":
        columns = ", ".join(data_dict.keys())
        placeholders = ", ".join("?" * len(data_dict))
        cursor.execute(f"INSERT INTO {TABLE_NAME} ({columns}) VALUES ({placeholders})", tuple(data_dict.values()))
        st.success(f"✅ Added new facility: {data_dict['FacilityID']}")
    else:
        set_str = ", ".join([f"{k} = ?" for k in data_dict.keys() if k != "FacilityID"])
        values = [v for k,v in data_dict.items() if k != "FacilityID"]
        values.append(sel_facility)
        cursor.execute(f"UPDATE {TABLE_NAME} SET {set_str} WHERE FacilityID = ?", values)
        st.success(f"✅ Updated facility: {data_dict['FacilityID']}")

    conn.commit()
    st.rerun()

# -----------------------------
# Data Table
# -----------------------------
st.markdown("---")
st.subheader("📄 Facilities Records")
st.dataframe(df_f, use_container_width=True)
