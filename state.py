"""
state.py — Session state initialization for BalikGamit (Supabase Connected).
Call init_state() once at app startup.
"""

import base64
import json
import streamlit as st
import streamlit.components.v1 as components


def init_state() -> None:
    """Initialize all session state keys with defaults."""
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


def save_session_cookie(user: dict) -> None:
    """Save the logged-in user to localStorage via JS."""
    try:
        encoded = base64.b64encode(json.dumps(user).encode()).decode()
        components.html(f"""
            <script>
                localStorage.setItem('balikgamit_session', '{encoded}');
            </script>
        """, height=0)
    except Exception:
        pass


def clear_session_cookie() -> None:
    """Remove the session from localStorage on sign out."""
    try:
        components.html("""
            <script>
                localStorage.removeItem('balikgamit_session');
            </script>
        """, height=0)
    except Exception:
        pass


def get_cookie_controller():
    return None  # no longer used


def is_faculty() -> bool:
    """Helper check to verify if the logged-in profile has administrative clearance."""
    if not st.session_state.get("logged_in") or not st.session_state.get("current_user"):
        return False
    return st.session_state.current_user.get("role") == "faculty"