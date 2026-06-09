"""
CDMO Quotation Platform — Reusable UI Components
"""

import streamlit as st
from src.auth import get_current_user, logout


def inject_css():
    """Force white backgrounds + black text everywhere."""
    st.markdown("""
    <style>
        /* ══════════════════════════════════════════════════════
           GLOBAL — white bg, black text
           ══════════════════════════════════════════════════════ */
        .stApp, .main, .block-container {
            background-color: #ffffff !important;
            color: #111827 !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #fafbfc !important;
            border-right: 1px solid #e5e7eb !important;
        }
        section[data-testid="stSidebar"] * {
            color: #374151 !important;
        }
        section[data-testid="stSidebar"] a {
            color: #374151 !important;
        }
        section[data-testid="stSidebar"] a[aria-current="page"] {
            background-color: #eef2ff !important;
            color: #4f46e5 !important;
        }

        /* ── ALL text dark ─────────────────────────── */
        p, span, div, label, h1, h2, h3, h4, h5, h6,
        .stMarkdown, .stCaption, .stText {
            color: #111827 !important;
        }
        .stCaption { color: #6b7280 !important; }

        /* ── Inputs — white bg, black text, black border ── */
        input, textarea,
        [data-baseweb="input"],
        [data-baseweb="textarea"],
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {
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

        /* ── Selectbox ─────────────────────────────── */
        .stSelectbox [data-baseweb="select"],
        .stSelectbox [role="listbox"] {
            background-color: #ffffff !important;
            color: #111827 !important;
        }

        /* ── Buttons ────────────────────────────────── */
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
        .stButton > button[kind="secondary"]:hover {
            background-color: #f9fafb !important;
            border-color: #9ca3af !important;
        }

        /* ── DataFrames / Tables — white rows, black border ── */
        .stDataFrame {
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        .stDataFrame [data-testid="stTable"] {
            background-color: #ffffff !important;
        }
        .stDataFrame table {
            background-color: #ffffff !important;
            border-collapse: collapse !important;
        }
        .stDataFrame thead tr th {
            background-color: #f9fafb !important;
            color: #374151 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            padding: 10px 14px !important;
            border-bottom: 1px solid #e5e7eb !important;
            text-align: left !important;
        }
        .stDataFrame tbody tr td {
            background-color: #ffffff !important;
            color: #111827 !important;
            font-size: 13px !important;
            padding: 10px 14px !important;
            border-bottom: 1px solid #f3f4f6 !important;
        }
        .stDataFrame tbody tr:hover td {
            background-color: #fafbfc !important;
        }

        /* Cover ALL possible dataframe internal elements */
        .stDataFrame * {
            background-color: transparent !important;
        }
        .stDataFrame [data-testid="stTable"] *,
        .stDataFrame [data-testid="stTable"] table,
        .stDataFrame [data-testid="stTable"] thead,
        .stDataFrame [data-testid="stTable"] tbody,
        .stDataFrame [data-testid="stTable"] tr,
        .stDataFrame [data-testid="stTable"] th,
        .stDataFrame [data-testid="stTable"] td {
            background-color: #ffffff !important;
        }
        .stDataFrame [data-testid="stTable"] thead th {
            background-color: #f9fafb !important;
            color: #374151 !important;
        }
        .stDataFrame [data-testid="stTable"] tbody td {
            color: #111827 !important;
        }
        .stDataFrame [data-testid="stTable"] tbody tr:hover td {
            background-color: #fafbfc !important;
        }

        /* GlideDataEditor cells */
        .dvn-scroller, .dvn-scroll-inner,
        [class*="glide"], [class*="data-editor"],
        canvas, .dvn-stack {
            background-color: #ffffff !important;
        }

        /* ── Tabs ───────────────────────────────────── */
        .stTabs [data-baseweb="tab"] {
            color: #6b7280 !important;
            background: transparent !important;
        }
        .stTabs [aria-selected="true"] {
            color: #4f46e5 !important;
            font-weight: 600 !important;
            border-bottom-color: #4f46e5 !important;
        }

        /* ── Container with border ──────────────────── */
        .stContainer {
            background-color: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 10px !important;
        }

        /* ── Metrics ────────────────────────────────── */
        [data-testid="stMetric"] {
            background-color: #f9fafb !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
        }
        [data-testid="stMetric"] * { color: #111827 !important; }
        [data-testid="stMetric"] label, [data-testid="stMetricLabel"] { color: #6b7280 !important; }

        /* ── Form labels ────────────────────────────── */
        .stTextInput label, .stNumberInput label,
        .stTextArea label, .stSelectbox label {
            font-size: 12px !important;
            color: #374151 !important;
            font-weight: 500 !important;
        }

        /* ── Info/Warning/Error messages ────────────── */
        .stAlert { color: #111827 !important; }

        /* ── Hide Streamlit chrome ──────────────────── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        div[data-testid="stToolbar"] { display: none; }
        .stDeployButton { display: none; }
        .stActionButton { display: none; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Sidebar: page nav (auto) + user info + logout."""
    user = get_current_user()
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"👤 **{user['username']}**")
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
