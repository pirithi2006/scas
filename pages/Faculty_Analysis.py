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
TABLE_NAME = "Faculty"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
conn.commit()

# -----------------------------
# Load Data
# -----------------------------
df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)

st.set_page_config(page_title="SCAS - Faculty Analysis", layout="wide")
st.title("👩‍🏫 Faculty Analysis")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters - Faculty")
all_depts = sorted(df["Department"].dropna().unique())
sel_depts = st.sidebar.multiselect("Department(s)", all_depts)

df_f = df.copy()
if sel_depts:
    df_f = df_f[df_f["Department"].isin(sel_depts)]

# -----------------------------
# KPIs
# -----------------------------
n = len(df_f)
avg_exp = round(df_f["ExperienceYears"].mean(), 2) if n else 0
avg_salary = round(df_f["NetPayINR"].mean(), 2) if n else 0
top_dept = df_f["Department"].value_counts().idxmax() if n else "—"

total_hours = int(df_f["TotalHoursPerWeek"].sum()) if n else 0
avg_hours = round(df_f["TotalHoursPerWeek"].mean(), 2) if n else 0
total_classes = int(df_f["ClassesHandled"].sum()) if n else 0
total_students = int((df_f["ClassesHandled"] * df_f["StudentsPerClass"]).sum()) if n else 0
stud_fac_ratio = round(sdiv(total_students, n, 0), 2) if n else 0

phd_faculty = round(sdiv(len(df_f[df_f["Qualification"].str.contains("PhD", case=False, na=False)]), n, 0) * 100, 2) if n else 0
class_advisors = int((df_f["IsClassAdvisor"] == "Yes").sum()) if n else 0

max_salary = int(df_f["NetPayINR"].max()) if n else 0
min_salary = int(df_f["NetPayINR"].min()) if n else 0
avg_bonus_pct = round(((df_f["BonusINR"] / df_f["BaseSalaryINR"]) * 100).mean(), 2) if n else 0

top_researcher = (
    df_f.loc[df_f["ResearchPapersPublished"].idxmax(), "Name"]
    if n and df_f["ResearchPapersPublished"].notna().any()
    else "—"
)

# KPI layout
st.subheader("🎯 KPIs")
c1, c2, c3 = st.columns(3)
c1.metric("Total Faculty", n)
c1.metric("Top Department", top_dept)
c1.metric("Class Advisors", class_advisors)

c2.metric("Average Experience (Years)", avg_exp)
c2.metric("Average Salary (INR)", avg_salary)
c2.metric("Avg Bonus % of Base", avg_bonus_pct)

c3.metric("Max Salary (INR)", max_salary)
c3.metric("Min Salary (INR)", min_salary)
c3.metric("PhD Qualified %", phd_faculty)

c4, c5, c6 = st.columns(3)
c4.metric("Total Teaching Hours/Week", total_hours)
c4.metric("Avg Hours per Faculty", avg_hours)

c5.metric("Total Classes Handled", total_classes)
c5.metric("Total Students Covered", total_students)

c6.metric("Student-Faculty Ratio", stud_fac_ratio)
c6.metric("Top Researcher", top_researcher)

# -----------------------------
# Charts
# -----------------------------
st.markdown("---")
st.subheader("📈 Visualizations")
colA, colB = st.columns(2)
if n:
    fig1 = px.pie(df_f, names="Department", title="Faculty by Department")
    colA.plotly_chart(fig1, use_container_width=True)
    fig2 = px.histogram(df_f, x="ExperienceYears", nbins=20, title="Experience Distribution")
    colB.plotly_chart(fig2, use_container_width=True)

colC, colD = st.columns(2)
if n:
    fig3 = px.bar(df_f.groupby("Department")["NetPayINR"].mean().reset_index(),
                  x="Department", y="NetPayINR", title="Avg Salary by Department")
    colC.plotly_chart(fig3, use_container_width=True)
    fig4 = px.bar(df_f.groupby("Department")["ExperienceYears"].mean().reset_index(),
                  x="Department", y="ExperienceYears", title="Avg Experience by Department")
    colD.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# CRUD: Add / Edit Faculty (Moved Below Charts)
# -----------------------------
st.markdown("---")
st.subheader("✏️ Edit Faculty")

faculty_ids = ["—"] + df_f["FacultyID"].tolist()
sel_faculty = st.selectbox("Select Faculty to Edit", faculty_ids)

if sel_faculty != "—":
    fac_data = df[df["FacultyID"] == sel_faculty].iloc[0].to_dict()
else:
    fac_data = {col: "" for col in df.columns}

col1, col2, col3, col4 = st.columns(4)
name = col1.text_input("Name", fac_data.get("Name", ""))
department = col2.text_input("Department", fac_data.get("Department", ""))
experience = col3.number_input("Experience (Years)", min_value=0.0, max_value=60.0, value=safe_float(fac_data.get("ExperienceYears"), 0.0))
base_salary = col4.number_input("Base Salary INR", min_value=0.0, value=safe_float(fac_data.get("BaseSalaryINR"), 0.0))

col5, col6, col7, col8 = st.columns(4)
bonus = col5.number_input("Bonus INR", min_value=0.0, value=safe_float(fac_data.get("BonusINR"), 0.0))
net_pay = col6.number_input("Net Pay INR", min_value=0.0, value=safe_float(fac_data.get("NetPayINR"), 0.0))
total_hours_per_week = col7.number_input("Total Hours/Week", min_value=0.0, value=safe_float(fac_data.get("TotalHoursPerWeek"), 0.0))
classes_handled = col8.number_input("Classes Handled", min_value=0, value=safe_int(fac_data.get("ClassesHandled"), 0))

col9, col10, col11 = st.columns(3)
students_per_class = col9.number_input("Students per Class", min_value=0, value=safe_int(fac_data.get("StudentsPerClass"), 0))
qualification = col10.text_input("Qualification", fac_data.get("Qualification", ""))
is_class_advisor = col11.selectbox("Class Advisor", ["Yes", "No"], index=0 if fac_data.get("IsClassAdvisor","No")=="Yes" else 1)

research_papers = col9.number_input("Research Papers Published", min_value=0, value=safe_int(fac_data.get("ResearchPapersPublished"), 0))

if st.button("💾 Save Faculty"):
    data_dict = {
        "FacultyID": sel_faculty if sel_faculty != "—" else f"FAC{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
        "Name": name,
        "Department": department,
        "ExperienceYears": experience,
        "BaseSalaryINR": base_salary,
        "BonusINR": bonus,
        "NetPayINR": net_pay,
        "TotalHoursPerWeek": total_hours_per_week,
        "ClassesHandled": classes_handled,
        "StudentsPerClass": students_per_class,
        "Qualification": qualification,
        "IsClassAdvisor": is_class_advisor,
        "ResearchPapersPublished": research_papers
    }

    if sel_faculty == "—":
        columns = ", ".join(data_dict.keys())
        placeholders = ", ".join("?" * len(data_dict))
        cursor.execute(f"INSERT INTO {TABLE_NAME} ({columns}) VALUES ({placeholders})", tuple(data_dict.values()))
        st.success(f"✅ Added new faculty: {data_dict['Name']}")
    else:
        set_str = ", ".join([f"{k} = ?" for k in data_dict.keys() if k != "FacultyID"])
        values = [v for k,v in data_dict.items() if k != "FacultyID"]
        values.append(sel_faculty)
        cursor.execute(f"UPDATE {TABLE_NAME} SET {set_str} WHERE FacultyID = ?", values)
        st.success(f"✅ Updated faculty: {data_dict['Name']}")

    conn.commit()
    st.rerun()  # Refresh page

# -----------------------------
# Data Table
# -----------------------------
st.markdown("---")
st.subheader("📄 Faculty Records")
st.dataframe(df_f, use_container_width=True)
