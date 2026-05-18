"""
sidebar.py — Sidebar navigation for BalikGamit (Supabase Connected Schema compatible).
"""

import streamlit as st
from utils import icon, icon_html
from state import is_faculty
from db import supabase


def render_sidebar() -> None:
    with st.sidebar:
        user     = st.session_state.current_user
        initials = "".join(p[0] for p in user["name"].split()[:2]).upper()
        role_html = (
            '<span class="role-faculty">Faculty</span>'
            if user["role"] == "faculty"
            else '<span class="role-student">Student</span>'
        )

        try:
            items_resp = supabase.table("items").select("approved").execute()
            db_items = items_resp.data if items_resp.data else []
            pending_count  = sum(1 for it in db_items if not it.get("approved", False))
            approved_count = sum(1 for it in db_items if it.get("approved", False))
        except Exception:
            pending_count  = 0
            approved_count = 0

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid #E2E6EA;">
          <div style="width:34px;height:34px;background:#164EC6;border-radius:9px;
                      display:flex;align-items:center;justify-content:center;
                      box-shadow:0 2px 8px rgba(22,78,198,.3);">
            {icon("search", 18, "white")}
          </div>
          <div>
            <div style="font-weight:700;font-size:1rem;letter-spacing:-.03em;color:#111827;line-height:1.2;">BalikGamit</div>
            <div style="font-size:.68rem;color:#6B7280;margin-top:1px;">Campus Lost &amp; Found</div>
          </div>
        </div>

        <div style="background:#FAFBFC;border:1px solid #E2E6EA;border-radius:10px;padding:12px;margin-bottom:24px;display:flex;align-items:center;gap:12px;">
          <div style="width:36px;height:36px;border-radius:50%;background:#EEF3FF;color:#164EC6;font-weight:700;font-size:.84rem;
                      display:flex;align-items:center;justify-content:center;box-shadow:inset 0 0 0 1px rgba(22,78,198,.1);flex-shrink:0;">
            {initials}
          </div>
          <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
            <div style="font-weight:600;font-size:.84rem;color:#111827;line-height:1.2;overflow:hidden;text-overflow:ellipsis;">{user["name"]}</div>
            <div style="display:flex;align-items:center;gap:6px;margin-top:3px;">
              {role_html}
              <span style="font-size:11px;color:#9CA3AF;">&bull;</span>
              <span style="font-size:.7rem;color:#6B7280;font-family:'DM Mono',monospace;">{approved_count} live</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation page names must exactly match the routing keys in app.py
        navigation_pages = ["Home", "Browse Items", "Post an Item"]
        if is_faculty():
            navigation_pages.append("Admin Dashboard")

        for pg in navigation_pages:
            is_active  = (st.session_state.page == pg)
            btn_label  = f"  {pg}"

            if pg == "Admin Dashboard":
                if st.button(btn_label, key=f"nav_{pg}", use_container_width=True,
                             type="primary" if is_active else "secondary"):
                    st.session_state.page = pg
                    st.rerun()

                if pending_count > 0:
                    st.markdown(
                        f"""<div style="position:relative;margin-top:-34px;margin-bottom:10px;margin-right:12px;float:right;pointer-events:none;">
                              <span class="badge badge-pending" style="padding:2px 6px;border-radius:10px;font-size:9px;font-weight:700;">
                                {pending_count}
                              </span>
                            </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                if st.button(btn_label, key=f"nav_{pg}", use_container_width=True,
                             type="primary" if is_active else "secondary"):
                    st.session_state.page = pg
                    st.rerun()

       st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.show_logout_confirm = True

        if st.session_state.get("show_logout_confirm", False):
            st.markdown("---")
            st.warning("Are you sure you want to sign out?")
            c1, c2 = st.columns(2)
            if c1.button("Yes, Sign Out", type="primary", use_container_width=True):
                st.session_state.logged_in    = False
                st.session_state.current_user = None
                st.session_state.page         = "Home"
                st.session_state.show_logout_confirm = False
                st.rerun()
            if c2.button("Cancel", type="secondary", use_container_width=True):
                st.session_state.show_logout_confirm = False
                st.rerun()
