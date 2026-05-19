"""
app.py — BalikGamit: Campus Lost & Found System
Main entry point. Run with: streamlit run app.py
"""

import base64
import json
import streamlit as st
from streamlit_cookies_controller import CookieController

from utils import icon
from styles import inject_styles
from state import init_state
from auth import render_auth_gate
from sidebar import render_sidebar
from pages import home, browse, post_item, admin


# ─── Page config (must be first Streamlit call) ───────────────────────────────
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

# ─── Global CSS ───────────────────────────────────────────────────────────────
inject_styles()

# ─── Cookie controller ────────────────────────────────────────────────────────
controller = CookieController()

# ─── Cookie restore with two-pass render ─────────────────────────────────────
# On first load, cookies aren't ready yet — we mark that we need to check,
# then rerun once so the cookie controller has time to hydrate.
if "cookie_checked" not in st.session_state:
    st.session_state.cookie_checked = False

if not st.session_state.cookie_checked:
    st.session_state.cookie_checked = True
    try:
        cookie_val = controller.get("balikgamit_session")
        if cookie_val:
            user_data = json.loads(cookie_val)
            if user_data.get("email") and user_data.get("name") and user_data.get("role"):
                st.session_state.logged_in    = True
                st.session_state.current_user = user_data
                st.session_state.page         = st.session_state.get("page", "Home")
    except Exception:
        pass
    st.rerun()

# ─── Session state defaults ───────────────────────────────────────────────────
init_state()

# ─── Auth gate ────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    render_auth_gate()

# ─── Sidebar navigation ───────────────────────────────────────────────────────
render_sidebar()

# ─── Page routing ─────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "Home":
    home.render()
elif page == "Browse Items":
    browse.render()
elif page == "Post an Item":
    post_item.render()
elif page == "Admin Dashboard":
    admin.render()