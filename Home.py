"""
CDMO Quotation Management Platform — Entry Point
Auto-redirects to Product Management. No login required.
"""

import streamlit as st
from src.database import init_db

st.set_page_config(
    page_title="CDMO Quotation Platform",
    page_icon="📋",
    layout="wide",
)

init_db()

# Auto-redirect to Product Management
st.switch_page("pages/1_Product_Management.py")
