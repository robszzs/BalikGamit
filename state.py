"""
state.py — Session state initialization for BalikGamit (Supabase Connected).
Call init_state() once at app startup.
"""

import streamlit as st
from streamlit_cookies_controller import CookieController
import json


def get_cookie_controller():
    if "cookie_controller" not in st.session_state:
        st.session_state.cookie_controller = CookieController()
    return st.session_state.cookie_controller


def init_state() -> None:
    """Initialize all session state keys with defaults, restoring from cookies if available."""
    defaults = {
        "logged_in":            False,
        "current_user":         None,
        "auth_tab":             "login",
        "claiming_item_id":     None,
        "found_report_for_id":  None,
        "browse_page":          0,
        "last_filter_key":      "",
        "page":                 "Home",
        "show_logout_confirm":  False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # ── Restore session from cookie if not logged in ──────────────────────────
    if not st.session_state.logged_in:
        try:
            controller = get_cookie_controller()
            cookie_val = controller.get("balikgamit_session")
            if cookie_val:
                user_data = json.loads(cookie_val)
                if user_data.get("email") and user_data.get("name") and user_data.get("role"):
                    st.session_state.logged_in    = True
                    st.session_state.current_user = user_data
        except Exception:
            pass  # Cookie missing or invalid — just stay logged out


def save_session_cookie(user: dict) -> None:
    """Save the logged-in user to a browser cookie."""
    try:
        controller = get_cookie_controller()
        controller.set("balikgamit_session", json.dumps(user), max_age=60 * 60 * 24 * 7)  # 7 days
    except Exception:
        pass


def clear_session_cookie() -> None:
    """Remove the session cookie on sign out."""
    try:
        controller = get_cookie_controller()
        controller.remove("balikgamit_session")
    except Exception:
        pass


def is_faculty() -> bool:
    """Helper check to verify if the logged-in profile has administrative clearance."""
    if not st.session_state.get("logged_in") or not st.session_state.get("current_user"):
        return False
    return st.session_state.current_user.get("role") == "faculty"