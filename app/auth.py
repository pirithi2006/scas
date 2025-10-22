# ==========================================================
# 🔐 auth.py — Authentication and User Management
# ==========================================================
import streamlit as st
from user_db import verify_user, add_user, init_user_table

# Initialize user table
init_user_table()

def login_section():
    st.title("🔐 Smart Campus Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = verify_user(username, password)
        if role:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['role'] = role
            st.success(f"Welcome, {username} ({role})")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

def logout_section():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.success("Logged out successfully")
        st.rerun()

def create_user_section():
    st.subheader("👨‍🏫 Create Faculty Account (Admin Only)")
    new_username = st.text_input("New Faculty Username")
    new_password = st.text_input("New Faculty Password", type="password")

    if st.button("Create Faculty User"):
        if new_username and new_password:
            success = add_user(new_username, new_password, "faculty")
            if success:
                st.success(f"✅ Faculty user '{new_username}' created successfully!")
            else:
                st.error("❌ Username already exists!")
        else:
            st.warning("Please enter all fields")
