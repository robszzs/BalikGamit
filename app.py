"""
app.py — BalikGamit: Campus Lost & Found System
Main entry point. Run with: streamlit run app.py
"""

import base64
import json
import streamlit as st

from styles import inject_styles
from state import init_state
from auth import render_auth_gate
from sidebar import render_sidebar
from pages import home, browse, post_item, admin


st.set_page_config(
    page_title="BalikGamit — Campus Lost & Found",
    page_icon=(
        "data:image/svg+xml;base64,"
        + base64.b64encode(
            b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
            b'stroke="#164EC6" stroke-width="2"><circle cx="11" cy="11" r="8"/>'
            b'<line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
        ).decode()
    ),
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()
init_state()

# ── Restore session from ?s= query param ──────────────────────────────────────
# save_session_cookie() writes ?s=<base64 user json> into the URL after login.
# The browser keeps the full URL on reload, so we can always read it back.
# We do NOT clear it — keeping it in the URL is what makes reload work.
if not st.session_state.logged_in:
    raw = st.query_params.get("s", "")
    if raw:
        try:
            user_data = json.loads(base64.b64decode(raw).decode())
            if user_data.get("email") and user_data.get("name") and user_data.get("role"):
                st.session_state.logged_in    = True
                st.session_state.current_user = user_data
                st.session_state.page         = st.session_state.get("page", "Home")
        except Exception:
            pass

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    render_auth_gate()

render_sidebar()

page = st.session_state.page
if page == "Home":
    home.render()
elif page == "Browse Items":
    browse.render()
elif page == "Post an Item":
    post_item.render()
elif page == "Admin Dashboard":
    admin.render()