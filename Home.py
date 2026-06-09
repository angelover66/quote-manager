"""
CDMO Quotation Management Platform — Main Entry Point
Login page when unauthenticated, app navigation when logged in.
"""

import streamlit as st
from src.database import init_db
from src.auth import login, is_logged_in, logout, get_current_user

# Initialize database on first run
init_db()

# ─── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="CDMO Quotation Platform",
    page_icon="📋",
    layout="wide" if is_logged_in() else "centered",
    initial_sidebar_state="auto" if is_logged_in() else "collapsed",
)

# ─── Not logged in → show login page ────────────────────────
if not is_logged_in():
    st.markdown("""
    <style>
        .stApp { background: #f5f7fa; }
        header[data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

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

    st.stop()

# ─── Logged in → show app ───────────────────────────────────
# Inject global CSS
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

# ─── Sidebar ────────────────────────────────────────────────
user = get_current_user()
with st.sidebar:
    st.markdown("""
    <div style="padding: 4px 0 16px 0;">
        <div style="font-size:11px; color:#9ca3af; text-transform:uppercase;
                    letter-spacing:0.5px; font-weight:600;">NAVIGATION</div>
    </div>
    """, unsafe_allow_html=True)

    # Use Streamlit native navigation
    pg = st.navigation({
        "Main": [
            st.Page("pages/1_Product_Management.py", title="📦 Product Management", icon="📦"),
            st.Page("pages/2_Quotation_Management.py", title="📋 Quotation Management", icon="📋"),
        ]
    })

    # User info + logout at bottom
    st.markdown(f"""
    <div style="border-top:1px solid #f0f0f0; padding-top:12px; margin-top:16px;">
        <div style="font-size:12px; color:#6b7280;">👤 {user['username']}</div>
        <div style="font-size:10px; color:#d1d5db; text-transform:capitalize;">{user['role']}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Logout", use_container_width=True, type="secondary"):
        logout()
        st.rerun()

# ─── Run the selected page ──────────────────────────────────
pg.run()
