"""
CDMO Quotation Management Platform — Login Page
Role-based routing after authentication.
"""

import streamlit as st
from src.database import init_db
from src.auth import login, is_logged_in

st.set_page_config(
    page_title="CDMO Quotation Platform",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Initialize database on first run (creates tables + seeds demo data)
init_db()

# Custom CSS for centered login card
st.markdown("""
<style>
    .stApp { background: #f5f7fa; }
    div[data-testid="stForm"] {
        background: white;
        padding: 40px 32px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    header[data-testid="stHeader"] { display: none; }
</style>
""", unsafe_allow_html=True)

# If already logged in, redirect to first page
if is_logged_in():
    st.switch_page("pages/1_Product_Management.py")

# Login form — centered layout
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    st.markdown("""
    <div style="text-align:center; margin-bottom:28px; margin-top:80px;">
        <div style="width:48px; height:48px; background:#6366f1; border-radius:10px;
                    margin:0 auto 12px; display:flex; align-items:center; justify-content:center;
                    font-size:22px; color:white;">📋</div>
        <div style="font-size:20px; font-weight:700; color:#1a1a2e;">CDMO Quotation Platform</div>
        <div style="font-size:13px; color:#9ca3af; margin-top:4px;">Quotation Management System</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            elif login(username, password):
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

    st.markdown("""
    <div style="text-align:center; margin-top:16px; font-size:11px; color:#9ca3af;">
        Demo: <b>sales</b> / <b>reviewer</b> &nbsp;|&nbsp; Password: <b>123456</b>
    </div>
    """, unsafe_allow_html=True)
