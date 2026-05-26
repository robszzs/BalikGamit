"""
dialogs.py — Shared Streamlit dialog components for BalikGamit.
"""

import streamlit as st
from utils import icon, icon_html, badge, photo_html, CATEGORY_ICONS

@st.dialog("Sign Out")
def sign_out_confirm_dialog() -> None:
    st.markdown(
        "<p style='margin-bottom:20px;color:#374151;'>Are you sure you want to sign out of your account?</p>",
        unsafe_allow_html=True,
    )
    col_cancel, col_confirm = st.columns(2)
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col_confirm:
        if st.button("Sign Out", use_container_width=True, type="primary"):
            from state import clear_session_cookie
            clear_session_cookie()  # ← clear the cookie on sign out
            st.session_state.logged_in    = False
            st.session_state.current_user = None
            st.session_state.page         = "Home"
            st.rerun()

@st.dialog("Create Faculty Account")
def create_faculty_dialog() -> None:
    with st.form("faculty_reg_form"):
        reg_name  = st.text_input("Full Name", placeholder="e.g. Maria Santos")
        reg_email = st.text_input("RTU Email", placeholder="0000-000000@rtu.edu.ph")
        reg_pw    = st.text_input("Password", type="password")
        reg_pw2   = st.text_input("Confirm Password", type="password")
        reg_btn   = st.form_submit_button("Create Faculty Account", type="primary", use_container_width=True)

    if reg_btn:
        from utils import EMAIL_PATTERN, _hash
        from db import supabase
        email_lc = reg_email.strip().lower()
        if not reg_name.strip():
            st.error("Please enter a full name.")
        elif not EMAIL_PATTERN.match(email_lc):
            st.error("Email must be in XXXX-XXXXXX@rtu.edu.ph format.")
        elif len(reg_pw) < 6:
            st.error("Password must be at least 6 characters.")
        elif reg_pw != reg_pw2:
            st.error("Passwords do not match.")
        else:
            check = supabase.table("users").select("email").eq("email", email_lc).execute()
            if check.data:
                st.error("An account with that email already exists.")
            else:
                supabase.table("users").insert({
                    "email":   email_lc,
                    "name":    reg_name.strip(),
                    "role":    "faculty",
                    "pw_hash": _hash(reg_pw),
                    "status":  "active"
                }).execute()
                st.success(f"Faculty account created for {reg_name.strip()}!")

@st.dialog("Item Details", width="large")
def item_detail_dialog(item: dict) -> None:
    cat_icon_name = CATEGORY_ICONS.get(item.get("category", "Other"), "package")

    if item.get("photo"):
        st.markdown(photo_html(item["photo"], width="100%", height="320px", radius="12px"), unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    else:
        st.markdown(photo_html(None, width="100%", height="120px", radius="12px", placeholder_text="No photo uploaded"), unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""<div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px;'>
          {badge(item['status'])}
          <span style='display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:700;color:#164EC6;
                       text-transform:uppercase;letter-spacing:.06em;'>
            {icon(cat_icon_name, 13, "#164EC6")} {item.get('category','—')}
          </span>
          <code style='margin-left:auto;font-size:.72rem;'>{item.get('id','—')}</code>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(f"### {item.get('title', 'Untitled Item')}")

    col_l, col_r = st.columns(2)
    col_l.markdown(
        f'<div style="display:flex;align-items:center;gap:6px;font-size:.875rem;">'
        f'{icon_html("map-pin",14,"#6B7280")} <strong>Location:</strong>&nbsp;{item.get("location","—")}</div>',
        unsafe_allow_html=True,
    )
    col_r.markdown(
        f'<div style="display:flex;align-items:center;gap:6px;font-size:.875rem;">'
        f'{icon_html("calendar",14,"#6B7280")} <strong>Date:</strong>&nbsp;{item.get("date","—")}</div>',
        unsafe_allow_html=True,
    )

    if item.get("marks"):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:6px;font-size:.875rem;margin-top:6px;">'
            f'{icon_html("tag",14,"#6B7280")} <strong>Identifying marks:</strong>&nbsp;{item["marks"]}</div>',
            unsafe_allow_html=True,
        )
    if item.get("contact"):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:6px;font-size:.875rem;margin-top:6px;">'
            f'{icon_html("mail",14,"#6B7280")} <strong>Contact:</strong>&nbsp;{item["contact"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    
    if item.get("status") == "lost":
        if st.button("I Found This", type="primary", use_container_width=True):
            st.session_state.found_report_for_id = item["id"]
            st.session_state.page = "Browse Items"
            st.rerun()
    
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:6px;font-weight:600;font-size:.875rem;margin-bottom:6px;">'
        f'{icon_html("file-text",14,"#374151")} Full Description</div>',
        unsafe_allow_html=True,
    )
    note = item.get("note") or "No additional details provided."
    # Format: replace ". " between known fields with line breaks for readability
    formatted = note.replace("Condition: ", "<b>Condition:</b> ")                     .replace(". Status details: ", "<br><br><b>Where it is now:</b> ")                     .replace(". Additional notes:", "<br><br><b>Additional notes:</b>")                     .replace("Where it is now: ", "<b>Where it is now:</b> ")                     .replace("Additional notes: ", "<b>Additional notes:</b> ")
    st.markdown(
        f'<div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:10px;'        f'padding:14px 16px;font-size:.88rem;color:#374151;line-height:1.8;">'        f'{formatted}'        f'</div>',
        unsafe_allow_html=True,
    )
