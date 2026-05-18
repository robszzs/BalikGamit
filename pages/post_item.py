"""
pages/post_item.py — Post a Lost or Found Item page for BalikGamit (Supabase Connected).
"""

import streamlit as st
from datetime import date
import base64
from utils import icon, icon_html, photo_html, resize_image, CATEGORY_ICONS
from db import supabase


def render() -> None:
    st.markdown(
        f'<span class="section-label">{icon_html("upload",11,"#164EC6","margin-right:4px;")} New Report</span>',
        unsafe_allow_html=True,
    )
    st.title("Post a Lost or Found Item")
    st.caption("Add as much detail as possible — clear photos and accurate locations dramatically improve recovery rates.")
    st.markdown("---")

    form_col, tip_col = st.columns([2, 1])

    with form_col:
        post_photo = st.file_uploader(
            "Photo of the item (JPG or PNG, max 5 MB)",
            type=["jpg", "jpeg", "png"],
            key="post_item_photo",
        )
        preview_bytes = None
        if post_photo:
            preview_bytes = resize_image(post_photo)
            st.markdown(photo_html(preview_bytes, width="260px", height="180px"), unsafe_allow_html=True)
            st.caption("Preview — this photo will be shown publicly.")

        with st.form("post_form", clear_on_submit=True):
            report_type = st.radio("Report type", ["I lost something", "I found something"], horizontal=True)
            item_type   = "lost" if "lost" in report_type else "found"
            st.markdown("<br>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                item_name = st.text_input("Item Name", placeholder="e.g. Black leather wallet")
            with col_b:
                category  = st.selectbox("Category", ["Wallet", "Gadget", "Accessory", "Book", "ID", "Stationery", "Clothing", "Other"])

            location_label = "Last Seen Location" if item_type == "lost" else "Where You Found It"
            location       = st.text_input(location_label, placeholder="e.g. Library, 2nd floor near study area B")

            col_c, col_d = st.columns(2)
            with col_c:
                report_date = st.date_input("Date", value=date.today())
            with col_d:
                marks = st.text_input("Identifying Marks", placeholder="Color, stickers, name, scratches…")

            description = st.text_area(
                "Description",
                placeholder="Add any details that help identify or verify ownership.",
                height=120,
                max_chars=600,
            )

            submitted = st.form_submit_button("Submit Report to Coordinators", type="primary", use_container_width=True)

            if submitted:
                if not item_name.strip() or not location.strip():
                    st.error("Please fulfill all mandatory properties (Item Name & Location parameters).")
                else:
                    try:
                        photo_str = None
                        if preview_bytes:
                            photo_str = base64.b64encode(preview_bytes).decode('utf-8')

                        # Column names exactly match the DB schema
                        item_row = {
                            "status": item_type,
                            "title": item_name.strip(),
                            "category": category,
                            "location": location.strip(),
                            "incident_date": report_date.strftime("%b %d"),
                            "marks": marks.strip(),
                            "description": description.strip(),
                            "contact": st.session_state.current_user["email"],
                            "reporter_email": st.session_state.current_user["email"],
                            "approved": False,
                            "photo_url": photo_str,
                        }

                        supabase.table("items").insert(item_row).execute()
                        st.success("Success! Your report was submitted and will be visible once approved by a faculty coordinator.")
                    except Exception as e:
                        st.error(f"Supabase Database writing failure: {e}")

    with tip_col:
        st.markdown(f"""
        <div style="background:#FFFDF5;border:1px solid #FDE68A;border-radius:var(--radius-lg);padding:1.2rem;box-shadow:var(--shadow-sm);">
          <div style="display:flex;align-items:center;gap:6px;font-size:.68rem;font-weight:700;
                      text-transform:uppercase;letter-spacing:.1em;color:#164EC6;margin-bottom:.6rem;">
            {icon("activity", 11, "#164EC6")} Preview Status
          </div>
          <span class="badge badge-pending">{icon("clock", 10, "#92400E")}&nbsp;PENDING</span>
          <div style="font-size:.78rem;color:#6B7280;margin-top:.6rem;line-height:1.55;">
            Once approved, your post becomes visible in <strong style="color:#111">Browse</strong> and can receive claim or found reports.
          </div>
        </div>
        """, unsafe_allow_html=True)
