# ==========================================================
# 🎯 app.py — SCAPS Main Login Page
# ==========================================================
import streamlit as st
from auth import login_section, logout_section
from user_db import init_user_table

st.set_page_config(page_title="SCAPS", layout="wide")
init_user_table()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_section()
else:
    st.sidebar.title("📊 SCAPS Navigation")
    logout_section()

    st.title("🎓 Smart Campus Analytics & Prediction System")
    st.caption(f"Logged in as: **{st.session_state['username']} ({st.session_state['role']})**")

    st.info("""
    👉 Use the sidebar or the **Pages** menu (on the left panel) to explore:
    - Canteen Insights
    - Students Analytics
    - Facility Analytics
    - Faculty Analytics
    - Energy Usage
    """)

    if st.session_state['role'] == 'admin':
        from auth import create_user_section
        st.divider()
        create_user_section()
