# app.py
import pandas as pd # For Data Manipulation
import streamlit as st
import plotly.express as px
import sqlite3


DB_PATH = "datascas.db"
S_TN = "Students"
F_TN = "Faculty"
FS_TN = "Facilities"

# -----------------------------
# Connect to DB
# -----------------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

st.set_page_config(page_title="SCAS - Overall Summary", layout="wide")

# -----------------------------
# Load Data
# -----------------------------
students = pd.read_sql(f"SELECT * FROM {S_TN}", conn)
faculty = pd.read_sql(f"SELECT * FROM {F_TN}", conn)
facilities = pd.read_sql(f"SELECT * FROM {FS_TN}", conn)
st.title("📊 SCAS - Overall Campus Summary")

# -----------------------------
# Sidebar Filters (empty = show all)
# -----------------------------
st.sidebar.header("🔍 Global Filters")

# Year (only if present)
if "Year" in students.columns:
    all_years = sorted(students["Year"].dropna().unique())
    sel_years = st.sidebar.multiselect("Year(s)", all_years)
else:
    sel_years = []

# Program filter (Students)
all_programs = sorted(students["Program"].dropna().unique())
sel_programs = st.sidebar.multiselect("Program(s)", all_programs)

# Department filter (Faculty)
all_depts = sorted(faculty["Department"].dropna().unique())
sel_depts = st.sidebar.multiselect("Department(s)", all_depts)

# Facility Type filter (Facilities)
all_ftypes = sorted(facilities["FacilityType"].dropna().unique())
sel_ftypes = st.sidebar.multiselect("Facility Type(s)", all_ftypes)

# Apply filters (only if user picked something)
students_f = students.copy()
faculty_f = faculty.copy()
facilities_f = facilities.copy()

if sel_years and "Year" in students_f.columns:
    students_f = students_f[students_f["Year"].isin(sel_years)]
if sel_programs:
    students_f = students_f[students_f["Program"].isin(sel_programs)]
if sel_depts:
    faculty_f = faculty_f[faculty_f["Department"].isin(sel_depts)]
if sel_ftypes:
    facilities_f = facilities_f[facilities_f["FacilityType"].isin(sel_ftypes)]

# -----------------------------
# Helper: safe division
# -----------------------------
def sdiv(a, b, default=0.0):
    try:
        return a / b if b else default
    except Exception:
        return default

# -----------------------------
# KPI Cards (Overall)
# -----------------------------
# Students
total_students = len(students_f)
avg_Cgpa = round(students_f["CGPA"].mean(), 2) if total_students else 0
avg_att = round(students_f["AttendancePercent"].mean(), 2) if total_students else 0
pass_rate = round(sdiv(len(students_f[students_f["CGPA"] >= 6.0]), total_students, 0) * 100, 2) if total_students else 0
grad_rate = round(sdiv(len(students_f[students_f["Status"] == "Graduated"]), total_students, 0) * 100, 2) if total_students else 0
drop_rate = round(sdiv(len(students_f[students_f["Status"] == "Dropped"]), total_students, 0) * 100, 2) if total_students else 0
total_pending_fees = int(students_f["PendingFeeINR"].sum()) if "PendingFeeINR" in students_f.columns else 0
at_risk = round(sdiv(len(students_f[students_f["CGPA"] < 7.0]), total_students, 0) * 100, 2) if total_students else 0

# Faculty
total_faculty = len(faculty_f)
avg_exp = round(faculty_f["ExperienceYears"].mean(), 2) if total_faculty else 0
faculty_student_ratio = round(sdiv(total_students, total_faculty, 0), 2) if total_faculty else 0
avg_hours_week = round(faculty_f["TotalHoursPerWeek"].mean(), 2) if total_faculty else 0
phd_rate = round(sdiv(len(faculty_f[faculty_f["Qualification"] == "PhD"]), total_faculty, 0) * 100, 2) if "Qualification" in faculty_f.columns and total_faculty else 0

# Facilities
total_facilities = len(facilities_f)
avg_daily_users = round(facilities_f["AverageDailyUsers"].mean(), 2) if total_facilities else 0
avg_util = round((facilities_f["AverageDailyUsers"] / facilities_f["Capacity"] * 100).mean(), 2) if total_facilities else 0
good_count = int((facilities_f["MaintenanceStatus"] == "Good").sum()) if total_facilities else 0
repair_count = int((facilities_f["MaintenanceStatus"] == "Needs Repair").sum()) if total_facilities else 0
good_percent = round(sdiv(good_count, total_facilities, 0) * 100, 2) if total_facilities else 0
avg_usage_hours = round(facilities_f["UsageHoursPerDay"].mean(), 2) if total_facilities else 0
top_facility = (
    facilities_f.groupby("FacilityType")
    .apply(lambda x: (x["AverageDailyUsers"].sum() / x["Capacity"].sum()) * 100)
    .idxmax()
    if total_facilities else "N/A"
)

# Layout KPIs
st.subheader("🎯 Overall KPIs")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Students", total_students)
c1.metric("Avg CGPA", avg_Cgpa)
c1.metric("Avg Attendance %", avg_att)
c1.metric("💰 Total Pending Fees", f"₹{total_pending_fees:,}")  # NEW KPI
c2.metric("Pass Rate % (CGPA≥6.0)", pass_rate)
c2.metric("Graduation Rate %", grad_rate)
c2.metric("Dropout Rate %", drop_rate)
c2.metric("At-Risk Students % (CGPA<7.0)", f"{at_risk}%")
c3.metric("Total Faculty", total_faculty)
c3.metric("Faculty / Student Ratio", faculty_student_ratio)
c3.metric("Avg Weekly Hours (Faculty)", avg_hours_week)
c3.metric("PhD Holders %", phd_rate)     # NEW
c4.metric("Total Facilities", total_facilities)
c4.metric("Avg Daily Users", avg_daily_users)
c4.metric("Avg Capacity Utilization", f"{avg_util}%")
c4.metric("Facilities Needing Repair", repair_count)
# -----------------------------
# Top-level Visuals
# -----------------------------
st.markdown("---")
st.subheader("📈 Quick Distributions")

colA, colB = st.columns(2)
with colA:
    if len(students_f):
        fig1 = px.pie(students_f, names="Program", title="Students by Program")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No student data for current filters.")
with colB:
    if len(faculty_f):
        dept_counts = faculty_f["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        fig2 = px.bar(dept_counts, x="Department", y="Count", title="Faculty by Department")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No faculty data for current filters.")

colC, colD = st.columns(2)
with colC:
    if len(facilities_f):
        fig3 = px.bar(facilities_f, x="FacilityType", y="UsageHoursPerDay", title="Usage Hours per Day by Facility Type")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No facilities data for current filters.")
with colD:
    if len(students_f):
        fig4 = px.histogram(students_f, x="CGPA", nbins=20, title="CGPA Distribution")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No student data for CGPA distribution.")

# -----------------------------
# Pending Fees by Program
# -----------------------------
st.markdown("---")
st.subheader("💰 Pending Fees Analysis")

if len(students_f) and "Program" in students_f.columns and "PendingFeeINR" in students_f.columns:
    fees_by_prog = students_f.groupby("Program")["PendingFeeINR"].sum().reset_index()
    fig5 = px.bar(
        fees_by_prog,
        x="Program",
        y="PendingFeeINR",
        title="Pending Fees by Program",
        text_auto=True
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Show student-level table
    st.markdown("### 📋 Student-Level Pending Fees")
    pending_table = students_f[["StudentID", "Name", "Program", "Year", "TotalFeeINR", "FeePaidINR", "PendingFeeINR", "FeeStatus"]]
    st.dataframe(pending_table, use_container_width=True)

    # CSV download button
    csv = pending_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Pending Fees Data as CSV",
        data=csv,
        file_name="pending_fees_report.csv",
        mime="text/csv"
    )
else:
    st.info("No fee data available for current filters.")
