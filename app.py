"""
app.py — BalikGamit: Campus Lost & Found System
Main entry point. Run with: streamlit run app.py
"""

import base64
import streamlit as st

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

# ─── Session state defaults ───────────────────────────────────────────────────
init_state()

# ─── Auth gate ────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    render_auth_gate()          # calls st.stop() internally          # calls st.stop() internally

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
