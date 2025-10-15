import streamlit as st
import pandas as pd
import sqlite3

# -----------------------------
# DB Config
# -----------------------------
DB_PATH = "datascas.db"

st.set_page_config(page_title="Upload Updated Lists", layout="wide")
st.title("📤 Upload Updated Lists")

# -----------------------------
# Helper function to upload
# -----------------------------
def upload_to_db(file, table_name):
    if file is None:
        st.warning("No file uploaded!")
        return

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.success(f"✅ {table_name} file loaded. Preview:")
    st.dataframe(df.head())

    if st.button(f"💾 Save {table_name} to Database", key=table_name):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute(f"DELETE FROM {table_name}")

        # Insert new data
        placeholders = ", ".join(["?"] * len(df.columns))
        columns = ", ".join(df.columns)
        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
                tuple(row)
            )

        conn.commit()
        conn.close()
        st.success(f"✅ Updated {table_name} saved to database!")

# -----------------------------
# Upload sections
# -----------------------------

col1,col2,col3 = st.columns(3)
with col1:
    st.header("📄 Upload Students List")
    student_file = st.file_uploader("Upload Students CSV/XLSX", type=["csv", "xlsx"], key="students")
    upload_to_db(student_file, "Students")
    st.markdown("---")

with col2:
    st.header("👩‍🏫 Upload Faculty List")
    faculty_file = st.file_uploader("Upload Faculty CSV/XLSX", type=["csv", "xlsx"], key="faculty")
    upload_to_db(faculty_file, "Faculty")
    st.markdown("---")

with col3:
    st.header("🏢 Upload Facilities List")
    facilities_file = st.file_uploader("Upload Facilities CSV/XLSX", type=["csv", "xlsx"], key="facilities")
    upload_to_db(facilities_file, "Facilities")
    st.markdown("---")
