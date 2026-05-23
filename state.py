"""
state.py — Session state initialization for BalikGamit.
"""

import base64
import json
import streamlit as st


def init_state() -> None:
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
    """Write user data into the URL as ?s=<base64>."""
    try:
        encoded = base64.b64encode(json.dumps(user).encode()).decode()
        st.query_params["s"] = encoded
    except Exception:
        pass


def save_page(page: str) -> None:
    """Keep the current page in the URL so reload lands on the same tab."""
    try:
        st.query_params["p"] = page
    except Exception:
        pass


def clear_session_cookie() -> None:
    """Remove session from URL on logout."""
    try:
        st.query_params.clear()
    except Exception:
        pass


def get_cookie_controller():
    return None


def is_faculty() -> bool:
    if not st.session_state.get("logged_in") or not st.session_state.get("current_user"):
        return False
    return st.session_state.current_user.get("role") == "faculty"