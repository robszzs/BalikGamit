"""
state.py — Session state initialization for BalikGamit (Supabase Connected).
Call init_state() once at app startup.
"""

import streamlit as st


def init_state() -> None:
    """Initialize all session state keys with defaults if not already set."""
    if "logged_in"           not in st.session_state: st.session_state.logged_in            = False
    if "current_user"        not in st.session_state: st.session_state.current_user         = None
    if "auth_tab"            not in st.session_state: st.session_state.auth_tab             = "login"
    
    # Supabase layout trackers
    if "claiming_item_id"    not in st.session_state: st.session_state.claiming_item_id     = None
    if "found_report_for_id" not in st.session_state: st.session_state.found_report_for_id = None
    if "browse_page"         not in st.session_state: st.session_state.browse_page          = 0
    if "last_filter_key"     not in st.session_state: st.session_state.last_filter_key      = ""
    if "page"                not in st.session_state: st.session_state.page                 = "Home"
    if "show_logout_confirm" not in st.session_state: st.session_state.show_logout_confirm  = False
    if "page"                not in st.session_state: st.session_state.page                 = "Home"
    # ADD THIS LINE BELOW:
    if "show_logout_confirm" not in st.session_state: st.session_state.show_logout_confirm  = False


def is_faculty() -> bool:
    """Helper check to verify if the logged-in profile has administrative clearance."""
    if not st.session_state.get("logged_in") or not st.session_state.get("current_user"):
        return False
    return st.session_state.current_user.get("role") == "faculty"
    
