"""
CDMO Quotation Platform — Reusable UI Components
Sidebar user info, CSS styling, display helpers.
"""

import streamlit as st
from src.auth import get_current_user, logout


def inject_css():
    """Inject global CSS styles matching the Clean Light + Indigo design system."""
    st.markdown("""
    <style>
        .stApp { background: #f5f7fa; }

        section[data-testid="stSidebar"] {
            background: white;
            border-right: 1px solid #f0f0f0;
        }

        .stButton > button[kind="primary"] {
            background-color: #6366f1 !important;
            border: none !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        .stButton > button[kind="secondary"] {
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            color: #6b7280 !important;
            background: white !important;
        }

        .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
            font-size: 12px !important;
            color: #6b7280 !important;
            font-weight: 500 !important;
        }

        header[data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with user info and logout button.
    Page navigation is handled natively by Streamlit multi-page discovery."""
    user = get_current_user()
    with st.sidebar:
        # User info at top
        st.markdown(f"""
        <div style="padding: 8px 0 16px 0;">
            <div style="font-size:13px; font-weight:600; color:#1a1a2e;">👤 {user['username']}</div>
            <div style="font-size:11px; color:#9ca3af; text-transform:capitalize;">{user['role']}</div>
        </div>
        <div style="border-bottom:1px solid #f0f0f0; margin-bottom:12px;"></div>
        """, unsafe_allow_html=True)

        if st.button("Logout", use_container_width=True, type="secondary"):
            logout()
            st.switch_page("Home.py")


def status_badge(status: str) -> str:
    """Return HTML for a pill-shaped status badge."""
    mapping = {
        "active": ('#e0e7ff', '#4338ca', 'Active'),
        "inactive": ('#fef3c7', '#92400e', 'Inactive'),
        "submitted": ('#e0e7ff', '#4338ca', 'Submitted'),
        "draft": ('#fef3c7', '#92400e', 'Draft'),
    }
    bg, color, label = mapping.get(status.lower(), ('#f3f4f6', '#6b7280', status))
    return f'<span style="background:{bg}; color:{color}; padding:3px 8px; border-radius:10px; font-size:11px;">{label}</span>'


def format_price(amount) -> str:
    """Format a number as CNY price string."""
    if amount is None:
        return "—"
    if isinstance(amount, (int, float)):
        return f"¥{amount:,.0f}"
    return str(amount)
