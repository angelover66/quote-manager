"""
CDMO Quotation Platform — Reusable UI Components
"""

import streamlit as st
from src.auth import get_current_user, logout


def inject_css():
    """White theme CSS."""
    st.markdown("""
    <style>
        .stApp, .main, .block-container {
            background-color: #ffffff !important;
            color: #111827 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #fafbfc !important;
        }

        /* Native nav links — ensure visible */
        [data-testid="stSidebarNav"] a {
            color: #374151 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            color: #4f46e5 !important;
            font-weight: 700 !important;
        }

        /* Inputs */
        input, textarea, [data-baseweb="input"], [data-baseweb="textarea"],
        .stTextInput input, .stNumberInput input, .stTextArea textarea {
            background-color: #ffffff !important;
            color: #111827 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
        }
        input::placeholder, textarea::placeholder { color: #9ca3af !important; }

        /* Primary button */
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

        /* Tables */
        .stDataFrame {
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
        }
        .stDataFrame [data-testid="stTable"] table,
        .stDataFrame [data-testid="stTable"] th,
        .stDataFrame [data-testid="stTable"] td {
            background-color: #ffffff !important;
            color: #111827 !important;
        }
        .stDataFrame [data-testid="stTable"] th {
            background-color: #f9fafb !important;
            color: #374151 !important;
            font-weight: 600 !important;
        }

        /* Labels */
        .stTextInput label, .stNumberInput label,
        .stTextArea label, .stSelectbox label {
            font-size: 12px !important;
            color: #374151 !important;
            font-weight: 500 !important;
        }

        /* Hide Streamlit chrome */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        div[data-testid="stToolbar"] { display: none; }
        .stDeployButton { display: none; }
    </style>
    """, unsafe_allow_html=True)


def add_logout_button():
    """Add logout button at the bottom of the sidebar.
    Call this AFTER page content so it appears below Streamlit native nav."""
    user = get_current_user()
    with st.sidebar:
        st.divider()
        st.caption(f"👤 {user['username']} ({user['role']})")
        if st.button("Logout", use_container_width=True):
            logout()
            st.switch_page("Home.py")


def format_price(amount) -> str:
    if amount is None:
        return "—"
    if isinstance(amount, (int, float)):
        return f"¥{amount:,.0f}"
    return str(amount)
