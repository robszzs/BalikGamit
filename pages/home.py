"""
pages/home.py — Home page for BalikGamit (Supabase Connected).
"""

import streamlit as st
import base64
from utils import icon, icon_html, badge, photo_html, truncate, CATEGORY_ICONS
from dialogs import item_detail_dialog
from db import supabase


def render() -> None:
    st.markdown(f"""
    <div class="hero-banner">
      <div style="display:inline-flex;align-items:center;gap:6px;font-size:.68rem;font-weight:700;
                  text-transform:uppercase;letter-spacing:.1em;color:#F5C800;
                  background:rgba(245,200,0,.12);border:1px solid rgba(245,200,0,.25);
                  padding:4px 12px;border-radius:6px;margin-bottom:14px;">
        {icon("bar-chart", 11, "#F5C800")} Rizal Technological University
      </div>
      <h1>A smarter way to<br><span style="color:#F5C800;">recover</span> lost items<br>on campus.</h1>
      <p><strong style="color:white;font-weight:600;">BalikGamit</strong> is RTU's web-based Lost &amp; Found platform —
      connecting students and faculty to report, search, and reclaim lost belongings in one organized place.</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch records safely from Supabase
    try:
        all_items_resp = supabase.table("items").select("*").execute()
        all_items = all_items_resp.data if all_items_resp.data else []
    except Exception as e:
        st.error(f"Error fetching dashboard metrics: {e}")
        all_items = []

    approved_items = [it for it in all_items if it.get("approved", False)]
    total     = len(approved_items)
    n_pending = len([it for it in all_items if not it.get("approved", False)])
    n_lost    = sum(1 for i in approved_items if i["status"] == "lost")
    n_found   = sum(1 for i in approved_items if i["status"] == "found")
    n_claimed = sum(1 for i in approved_items if i["status"] == "claimed")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Reports",  total)
    c2.metric("Pending Review", n_pending)
    c3.metric("Lost",           n_lost)
    c4.metric("Found",          n_found)
    c5.metric("Returned",       n_claimed)

    st.markdown("<br>", unsafe_allow_html=True)

    col_feed, col_nav = st.columns([2, 1])

    with col_feed:
        st.markdown(
            f'<span class="section-label">{icon_html("clipboard",11,"#164EC6","margin-right:4px;")} Recent Reports</span>',
            unsafe_allow_html=True,
        )
        st.subheader("Latest Activity")

        recent = sorted(approved_items, key=lambda x: x.get("created_at", ""), reverse=True)[:4]
        if not recent:
            st.info("No approved items yet. Check back after an admin reviews the board.")
        else:
            for item in recent:
                # Decode photo_url (base64 string) into bytes for rendering
                photo_bytes = None
                if item.get("photo_url"):
                    try:
                        photo_bytes = base64.b64decode(item["photo_url"])
                    except Exception:
                        photo_bytes = None

                # Build a dialog-compatible dict using correct DB column names
                compat_item = {
                    "id": item["id"],
                    "status": item["status"],
                    "title": item["title"],
                    "category": item.get("category"),
                    "location": item.get("location"),
                    "date": item.get("incident_date"),
                    "marks": item.get("marks"),
                    "photo": photo_bytes,
                    "note": item.get("description"),
                    "contact": item.get("contact") or item.get("reporter_email"),
                }

                with st.container():
                    f_col1, f_col2 = st.columns([1, 4])
                    with f_col1:
                        st.markdown(photo_html(photo_bytes, width="100%", height="75px", radius="8px"), unsafe_allow_html=True)
                    with f_col2:
                        st.markdown(f"**{item['title']}** &nbsp;{badge(item['status'])}", unsafe_allow_html=True)
                        st.markdown(
                            f"<small style='color:#6B7280;'>Category: {item.get('category','—')} &middot; Location: {item.get('location','—')} &middot; Date: {item.get('incident_date','—')}</small>",
                            unsafe_allow_html=True
                        )
                        if st.button("View Details", key=f"home_view_{item['id']}"):
                            item_detail_dialog(compat_item)

    with col_nav:
        st.markdown(
            f'<span class="section-label">{icon_html("navigation",11,"#164EC6","margin-right:4px;")} Quick Navigation</span>',
            unsafe_allow_html=True,
        )
        st.subheader("Get Started")
        if st.button("Browse Campus Board", use_container_width=True, type="primary"):
            st.session_state.page = "Browse Items"
            st.rerun()
        if st.button("Report Lost or Found Item", use_container_width=True):
            st.session_state.page = "Post an Item"
            st.rerun()
