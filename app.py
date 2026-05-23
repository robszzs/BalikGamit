"""
app.py — BalikGamit: Campus Lost & Found System
Main entry point. Run with: streamlit run app.py
"""

import base64
import json
import streamlit as st
import streamlit.components.v1 as components

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

# ─── localStorage-based session restore ───────────────────────────────────────
# On first run, inject a tiny JS component that reads localStorage and sends
# the stored session back to Streamlit via query params, then triggers a rerun.

if "ls_checked" not in st.session_state:
    st.session_state.ls_checked = False

if not st.session_state.ls_checked and not st.session_state.logged_in:
    # Check if query params already has the session (sent by the JS below)
    raw = st.query_params.get("s")
    if raw:
        try:
            user_data = json.loads(base64.b64decode(raw).decode())
            if user_data.get("email") and user_data.get("name") and user_data.get("role"):
                st.session_state.logged_in    = True
                st.session_state.current_user = user_data
                st.session_state.page         = "Home"
                st.query_params.clear()        # clean up the URL
        except Exception:
            pass
        st.session_state.ls_checked = True
    else:
        # Inject JS to read localStorage and push value into URL, triggering a rerun
        components.html("""
            <script>
                const val = localStorage.getItem('balikgamit_session');
                if (val) {
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('s', val);
                    window.parent.location.replace(url.toString());
                } else {
                    // Nothing in localStorage, mark as checked via query param
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('s', 'none');
                    window.parent.location.replace(url.toString());
                }
            </script>
        """, height=0)
        st.stop()
else:
    st.session_state.ls_checked = True

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