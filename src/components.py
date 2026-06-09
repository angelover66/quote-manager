"""
CDMO Quotation Platform — Reusable UI Components
"""

import streamlit as st
from src.auth import get_current_user, logout


def inject_css():
    """Force white backgrounds + black text everywhere."""
    st.markdown("""
    <style>
        .stApp, .main, .block-container {
            background-color: #ffffff !important;
            color: #111827 !important;
        }

        section[data-testid="stSidebar"] {
            background-color: #fafbfc !important;
            border-right: 1px solid #e5e7eb !important;
        }

        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: #111827 !important;
        }

        input, textarea, [data-baseweb="input"], [data-baseweb="textarea"],
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            background-color: #ffffff !important;
            color: #111827 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
        }
        input::placeholder, textarea::placeholder { color: #9ca3af !important; }
        input:focus, textarea:focus {
            border-color: #4f46e5 !important;
            box-shadow: 0 0 0 2px rgba(79,70,229,0.15) !important;
        }

        .stButton > button[kind="primary"] {
            background-color: #4f46e5 !important;
            border: none !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        .stButton > button[kind="secondary"] {
            background-color: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            color: #374151 !important;
        }

        /* DataFrames — white bg, black text, black borders */
        .stDataFrame {
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        .stDataFrame [data-testid="stTable"] table,
        .stDataFrame [data-testid="stTable"] thead,
        .stDataFrame [data-testid="stTable"] tbody,
        .stDataFrame [data-testid="stTable"] tr,
        .stDataFrame [data-testid="stTable"] th,
        .stDataFrame [data-testid="stTable"] td,
        .stDataFrame * {
            background-color: #ffffff !important;
        }
        .stDataFrame [data-testid="stTable"] thead th {
            background-color: #f9fafb !important;
            color: #374151 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            padding: 10px 14px !important;
            border-bottom: 1px solid #e5e7eb !important;
        }
        .stDataFrame [data-testid="stTable"] tbody td {
            color: #111827 !important;
            font-size: 13px !important;
            padding: 10px 14px !important;
            border-bottom: 1px solid #f3f4f6 !important;
        }
        .stDataFrame [data-testid="stTable"] tbody tr:hover td {
            background-color: #fafbfc !important;
        }

        .stTabs [data-testid="stTabs"] [aria-selected="true"] {
            color: #4f46e5 !important;
            font-weight: 600 !important;
        }

        .stContainer {
            background-color: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 10px !important;
        }

        [data-testid="stMetric"] {
            background-color: #f9fafb !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
        }
        [data-testid="stMetric"] * { color: #111827 !important; }

        .stTextInput label, .stNumberInput label,
        .stTextArea label, .stSelectbox label {
            font-size: 12px !important;
            color: #374151 !important;
            font-weight: 500 !important;
        }

        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        div[data-testid="stToolbar"] { display: none; }
        .stDeployButton { display: none; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Sidebar with explicit navigation links + user info."""
    user = get_current_user()
    with st.sidebar:
        st.markdown("""
        <div style="padding:8px 0 12px 0;margin-bottom:8px;border-bottom:1px solid #e5e7eb;">
            <div style="font-size:11px;color:#9ca3af;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">
                NAVIGATION</div>
        </div>
        """, unsafe_allow_html=True)

        # Explicit page links — always visible
        col1, col2 = st.columns(2)
        with col1:
            st.page_link("pages/1_Product_Management.py", label="📦 Products", use_container_width=True)
        with col2:
            st.page_link("pages/2_Quotation_Management.py", label="📋 Quotations", use_container_width=True)

        st.markdown("---")

        # User info
        st.markdown(f"👤 **{user['username']}**")
        st.caption(f"Role: {user['role']}")

        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.switch_page("Home.py")


def format_price(amount) -> str:
    if amount is None:
        return "—"
    if isinstance(amount, (int, float)):
        return f"¥{amount:,.0f}"
    return str(amount)
