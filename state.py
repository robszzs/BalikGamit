"""
state.py — Session state initialization for BalikGamit.
"""

import json
import secrets
import streamlit as st
from db import supabase


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
    """Create a random token, store it in Supabase, put it in the URL."""
    try:
        token = secrets.token_urlsafe(32)
        supabase.table("sessions").insert({
            "token": token,
            "user_data": json.dumps(user),
        }).execute()
        st.query_params["t"] = token
        st.query_params["p"] = st.session_state.get("page", "Home")
    except Exception:
        pass


def save_page(page: str) -> None:
    """Keep the current page in the URL."""
    try:
        st.query_params["p"] = page
    except Exception:
        pass


def clear_session_cookie() -> None:
    """Delete the token from Supabase so the link is dead, then clear URL."""
    try:
        token = st.query_params.get("t", "")
        if token:
            supabase.table("sessions").delete().eq("token", token).execute()
        st.query_params.clear()
    except Exception:
        pass


def get_cookie_controller():
    return None


def is_faculty() -> bool:
    if not st.session_state.get("logged_in") or not st.session_state.get("current_user"):
        return False
    return st.session_state.current_user.get("role") == "faculty"