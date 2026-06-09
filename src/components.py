"""
CDMO Quotation Platform — Reusable UI Components
"""

import streamlit as st
from src.auth import get_current_user, logout


def inject_css():
    """White minimal theme CSS."""
    st.markdown("""
    <style>
        /* ── Global ─────────────────────────────── */
        .stApp {
            background: #ffffff;
        }

        /* ── Sidebar ────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: #fafbfc;
            border-right: 1px solid #e5e7eb;
        }
        section[data-testid="stSidebar"] * {
            background-color: transparent !important;
        }
        section[data-testid="stSidebar"] .st-emotion-cache-1cypcdb {
            background: #fafbfc !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            background: #fafbfc !important;
            padding-top: 8px;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
            color: #374151 !important;
            font-size: 14px !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: #eef2ff !important;
            color: #4f46e5 !important;
            font-weight: 600 !important;
        }

        /* ── Inputs — white bg ──────────────────── */
        input, textarea, .stTextInput input, .stNumberInput input,
        [data-baseweb="input"], [data-baseweb="textarea"],
        .stSelectbox [role="listbox"], .stSelectbox [data-baseweb="select"] {
            background-color: #ffffff !important;
            color: #1a1a2e !important;
            border: 1px solid #d1d5db !important;
            border-radius: 6px !important;
        }
        input::placeholder, textarea::placeholder {
            color: #9ca3af !important;
        }

        /* ── Buttons ─────────────────────────────── */
        .stButton > button[kind="primary"] {
            background-color: #4f46e5 !important;
            border: none !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        .stButton > button[kind="secondary"] {
            background: white !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            color: #374151 !important;
        }

        /* ── DataFrames — white rows ─────────────── */
        .stDataFrame, [data-testid="stTable"] {
            background: white !important;
        }
        .stDataFrame table, [data-testid="stTable"] table {
            background: white !important;
        }
        .stDataFrame th, [data-testid="stTable"] th {
            background: #f9fafb !important;
            color: #6b7280 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
        }
        .stDataFrame td, [data-testid="stTable"] td {
            background: white !important;
            color: #1a1a2e !important;
            font-size: 13px !important;
        }

        /* ── Tabs ─────────────────────────────────── */
        .stTabs [data-baseweb="tab"] {
            color: #6b7280 !important;
            background: transparent !important;
        }
        .stTabs [aria-selected="true"] {
            color: #4f46e5 !important;
            font-weight: 600 !important;
        }

        /* ── Labels ──────────────────────────────── */
        .stTextInput label, .stNumberInput label,
        .stTextArea label, .stSelectbox label {
            font-size: 12px !important;
            color: #6b7280 !important;
            font-weight: 500 !important;
        }

        /* ── Metrics ─────────────────────────────── */
        [data-testid="stMetric"] {
            background: #f9fafb !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
        }

        /* ── Remove Streamlit defaults ────────────── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        div[data-testid="stToolbar"] { display: none; }
        .stDeployButton { display: none; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Sidebar: Streamlit auto-shows page nav above. We add user info + logout below."""
    user = get_current_user()
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"👤 **{user['username']}**  ")
        st.caption(f"Role: {user['role']}")
        if st.button("Logout", use_container_width=True):
            logout()
            st.switch_page("Home.py")


def format_price(amount) -> str:
    if amount is None:
        return "—"
    if isinstance(amount, (int, float)):
        return f"¥{amount:,.0f}"
    return str(amount)
