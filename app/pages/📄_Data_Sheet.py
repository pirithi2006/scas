import streamlit as st
import pandas as pd
from db import get_table
import sqlite3

st.title("📄 Data Sheet & Upload Data")

# Select dataset/table
dataset_options = ["students", "students_subjects" ,"faculty", "energy", "canteen", "facility_logs"]
selected_dataset = st.selectbox("Select Table / Dataset:", dataset_options)

# ===============================
# 1️⃣ Upload CSV to database
# ===============================
st.subheader("⬆️ Upload CSV to Table")

uploaded_file = st.file_uploader("Choose a CSV file to upload", type="csv")

if uploaded_file is not None:
    try:
        upload_df = pd.read_csv(uploaded_file)

        # Connect to DB
        conn = sqlite3.connect("SCAPS.db")
        c = conn.cursor()

        # Check table columns
        c.execute(f"PRAGMA table_info({selected_dataset})")
        table_columns = [info[1] for info in c.fetchall()]
        missing_cols = [col for col in table_columns if col not in upload_df.columns]

        if missing_cols:
            st.error(f"The uploaded CSV is missing these columns: {missing_cols}")
        else:
            if st.button("Upload to Database"):
                upload_df.to_sql(selected_dataset, conn, if_exists="replace", index=False)
                st.success(f"Data uploaded successfully to table '{selected_dataset}'!")

        conn.close()
    except Exception as e:
        st.error(f"Error: {e}")

# ===============================
# 2️⃣ Load current dataset
# ===============================
df = get_table(selected_dataset)

# ===============================
# 3️⃣ Filters (categorical only)
# ===============================
st.subheader("🔎 Filters")

categorical_cols = df.select_dtypes(include=['object', 'bool', 'category']).columns.tolist()
col_count = 3
cols = st.columns(col_count)
filter_values = {}

for i, col in enumerate(categorical_cols):
    with cols[i % col_count]:
        options = ["All"] + df[col].unique().tolist()
        selected = st.multiselect(f"{col}:", options, default=["All"])
        if "All" in selected:
            selected = df[col].unique().tolist()
        filter_values[col] = selected

# Apply filters
for col, val in filter_values.items():
    df = df[df[col].isin(val)]

# ===============================
# 4️⃣ Display filtered data
# ===============================
st.subheader(f"Filtered '{selected_dataset}' Data")
st.dataframe(df)

# ===============================
# 5️⃣ Download button
# ===============================
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name=f"{selected_dataset}_filtered.csv",
    mime="text/csv"
)
