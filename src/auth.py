"""
CDMO Quotation Platform — Authentication
Login/logout helpers, session state management, auth gate decorator.
"""

import streamlit as st
from src.database import verify_user


def is_logged_in() -> bool:
    """Check if user is authenticated in current session."""
    return "user" in st.session_state and st.session_state.user is not None


def require_auth():
    """Gate: if not logged in, redirect to login page."""
    if not is_logged_in():
        st.switch_page("Home.py")


def login(username: str, password: str) -> bool:
    """Attempt login. Stores user dict in session_state on success."""
    user = verify_user(username, password)
    if user:
        st.session_state.user = {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
        }
        return True
    return False


def logout():
    """Clear all session state keys."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def get_current_user():
    """Get current user from session, or None if not logged in."""
    return st.session_state.get("user")
