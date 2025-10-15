import pandas as pd
import streamlit as st
import plotly.express as px
import sqlite3

DB_PATH = "datascas.db"
TABLE_NAME = "Students"

# -----------------------------
# Connect to DB
# -----------------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Load students data from SQLite
df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)

st.set_page_config(page_title="SCAS - Student Analysis", layout="wide")
st.title("🎓 Student Analysis")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters - Students")
if "Year" in df.columns:
    all_years = sorted(df["Year"].dropna().unique())
    sel_years = st.sidebar.multiselect("Year(s)", all_years)
else:
    sel_years = []

all_programs = sorted(df["Program"].dropna().unique())
sel_programs = st.sidebar.multiselect("Program(s)", all_programs)

all_status = sorted(df["Status"].dropna().unique())
sel_status = st.sidebar.multiselect("Status", all_status)

# Apply filters
df_f = df.copy()
if sel_years and "Year" in df_f.columns:
    df_f = df_f[df_f["Year"].isin(sel_years)]
if sel_programs:
    df_f = df_f[df_f["Program"].isin(sel_programs)]
if sel_status:
    df_f = df_f[df_f["Status"].isin(sel_status)]

# -----------------------------
# Helper
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
# KPIs
# -----------------------------
n = len(df_f)
avg_gpa = round(df_f["CGPA"].apply(safe_float).mean(), 2) if n else 0
avg_att = round(df_f["AttendancePercent"].apply(safe_float).mean(), 2) if n else 0
pass_rate = round(sdiv(len(df_f[df_f["CGPA"].apply(safe_float) >= 2.0]), n, 0) * 100, 2) if n else 0
grad_rate = round(sdiv(len(df_f[df_f["Status"] == "Graduated"]), n, 0) * 100, 2) if n else 0
drop_rate = round(sdiv(len(df_f[df_f["Status"] == "Dropped"]), n, 0) * 100, 2) if n else 0
high_achievers = round(sdiv(len(df_f[df_f["CGPA"].apply(safe_float) >= 3.5]), n, 0) * 100, 2) if n else 0

top_program = df_f["Program"].value_counts().idxmax() if n else "—"
males = int((df_f["Gender"] == "Male").sum()) if n else 0
females = int((df_f["Gender"] == "Female").sum()) if n else 0
gender_ratio = f"{males} : {females}"

# Financial KPIs
total_fees = df_f["TotalFeeINR"].apply(safe_float).sum() if n and "TotalFeeINR" in df_f.columns else 0
pending_fees = df_f["PendingFeeINR"].apply(safe_float).sum() if n and "PendingFeeINR" in df_f.columns else 0
pending_percent = round(sdiv(pending_fees, total_fees, 0) * 100, 2) if total_fees else 0

# KPI layout
st.subheader("🎯 KPIs")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Students", n)
c1.metric("Top Program", top_program)
c1.metric("Gender Ratio (M:F)", gender_ratio)
c2.metric("Average GPA", avg_gpa)
c2.metric("Average Attendance %", avg_att)
c2.metric("High Achievers % (GPA ≥ 3.5)", high_achievers)
c3.metric("Pass Rate % (GPA ≥ 2.0)", pass_rate)
c3.metric("Graduation Rate %", grad_rate)
c3.metric("Dropout Rate %", drop_rate)
c4.metric("💰 Total Fees", f"{total_fees:,.0f}")
c4.metric("💸 Pending Fees", f"{pending_fees:,.0f}")
c4.metric("⏳ Pending %", f"{pending_percent}%")

# -----------------------------
# CRUD: Add / Edit Students
# -----------------------------
st.markdown("---")
st.subheader("✏️ Edit Students")

# Select student for edit
student_ids = ["—"] + df_f["StudentID"].tolist()
sel_student = st.selectbox("Select Student to Edit", student_ids)

if sel_student != "—":
    # Edit existing student
    student_data = df[df["StudentID"] == sel_student].iloc[0].to_dict()
else:
    # New student
    student_data = {col: "" for col in df.columns}

# Editable fields
cols1, cols2, cols3, cols4 = st.columns(4)
name = cols1.text_input("Name", student_data.get("Name", ""))
program = cols2.text_input("Program", student_data.get("Program", ""))
year = cols3.number_input(
    "Year", min_value=1, max_value=4,
    value=safe_int(student_data.get("Year"), 4)
)
cgpa = cols4.number_input(
    "CGPA", min_value=0.0, max_value=10.0,
    value=safe_float(student_data.get("CGPA"), 0.0)
)

cols5, cols6, cols7, cols8 = st.columns(4)
att = cols5.number_input(
    "Attendance %", min_value=0.0, max_value=100.0,
    value=safe_float(student_data.get("AttendancePercent"), 0.0)
)

# Safe Status selectbox
status_options = ["Active", "Graduated", "Dropped"]
status_value = student_data.get("Status", "Active")
if status_value not in status_options:
    status_value = "Active"
status = cols6.selectbox("Status", status_options, index=status_options.index(status_value))

total_fee = cols7.number_input(
    "Total Fee INR", min_value=0.0,
    value=safe_float(student_data.get("TotalFeeINR"), 0.0)
)
fee_paid = cols8.number_input(
    "Fee Paid INR", min_value=0.0,
    value=safe_float(student_data.get("FeePaidINR"), 0.0)
)

# Safe Gender selectbox
gender_options = ["Male", "Female"]
gender_value = student_data.get("Gender", "Male")
if gender_value not in gender_options:
    gender_value = "Male"
gender = st.selectbox("Gender", gender_options, index=gender_options.index(gender_value))

# Calculate Pending Fee
pending_fee = total_fee - fee_paid
fee_status = "Paid" if pending_fee <= 0 else "Pending"

# Update / Add button
if st.button("💾 Save Student"):
    data_dict = {
        "StudentID": sel_student if sel_student != "—" else f"STU{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
        "Name": name,
        "Program": program,
        "Year": year,
        "CGPA": cgpa,
        "AttendancePercent": att,
        "Status": status,
        "TotalFeeINR": total_fee,
        "FeePaidINR": fee_paid,
        "PendingFeeINR": pending_fee,
        "FeeStatus": fee_status,
        "Gender": gender
    }

    # Check if new student or update existing
    if sel_student == "—":
        # Insert new student
        columns = ", ".join(data_dict.keys())
        placeholders = ", ".join("?" * len(data_dict))
        cursor.execute(f"INSERT INTO {TABLE_NAME} ({columns}) VALUES ({placeholders})", tuple(data_dict.values()))
        st.success(f"✅ Added new student: {data_dict['Name']}")
    else:
        # Update existing student
        set_str = ", ".join([f"{k} = ?" for k in data_dict.keys() if k != "StudentID"])
        values = [v for k, v in data_dict.items() if k != "StudentID"]
        values.append(sel_student)
        cursor.execute(f"UPDATE {TABLE_NAME} SET {set_str} WHERE StudentID = ?", values)
        st.success(f"✅ Updated student: {data_dict['Name']}")

    conn.commit()
    st.rerun()

# -----------------------------
# Show Table
# -----------------------------
st.markdown("---")
st.subheader("📄 Student Records")
st.dataframe(df_f, use_container_width=True)

# Keep connection open for Streamlit rerun
# conn.close()
