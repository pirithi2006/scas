# ==========================================================
# 📘 db.py — Database Connection & Query Functions
# ==========================================================
import sqlite3
import pandas as pd

DB_PATH = "SCAPS.db"

# ✅ Get DB connection
def get_connection():
    return sqlite3.connect(DB_PATH)

# ✅ Fetch table as DataFrame
def get_table(table_name):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# ✅ Run custom query
def run_query(query):
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
