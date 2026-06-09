"""
CDMO Quotation Platform — Reusable UI Components
Sidebar navigation, CSS styling, display helpers.
"""

import streamlit as st
from src.auth import get_current_user, logout


def inject_css():
    """Inject global CSS styles matching the Clean Light + Indigo design system."""
    st.markdown("""
    <style>
        /* Page background */
        .stApp { background: #f5f7fa; }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: white;
            border-right: 1px solid #f0f0f0;
        }
        section[data-testid="stSidebar"] .st-emotion-cache-1cypcdb {
            background: white;
        }

        /* Primary button — Indigo */
        .stButton > button[kind="primary"] {
            background-color: #6366f1 !important;
            border: none !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        /* Secondary button */
        .stButton > button[kind="secondary"] {
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            color: #6b7280 !important;
            background: white !important;
        }

        /* Form labels */
        .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label {
            font-size: 12px !important;
            color: #6b7280 !important;
            font-weight: 500 !important;
        }

        /* Hide default Streamlit header */
        header[data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with navigation (2 items) and user info."""
    user = get_current_user()
    with st.sidebar:
        st.markdown("""
        <div style="padding: 4px 0 16px 0;">
            <div style="font-size:11px; color:#9ca3af; text-transform:uppercase;
                        letter-spacing:0.5px; font-weight:600;">NAVIGATION</div>
        </div>
        """, unsafe_allow_html=True)

        # Streamlit native navigation — 2 pages only
        st.navigation([
            st.Page("pages/1_Product_Management.py", title="📦 Product Management", icon="📦"),
            st.Page("pages/2_Quotation_Management.py", title="📋 Quotation Management", icon="📋"),
        ])

        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

        # User info footer
        st.markdown(f"""
        <div style="border-top:1px solid #f0f0f0; padding-top:12px; margin-top:auto;">
            <div style="font-size:12px; color:#6b7280;">👤 {user['username']}</div>
            <div style="font-size:10px; color:#d1d5db; text-transform:capitalize;">{user['role']}</div>
        </div>
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
