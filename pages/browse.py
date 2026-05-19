"""
pages/browse.py — Browse Items page for BalikGamit (Supabase Connected).
"""

import streamlit as st
from datetime import date
import base64
from utils import (
    icon, icon_html, badge, photo_html, truncate,
    CATEGORY_ICONS, ITEMS_PER_PAGE, resize_image,
)
from dialogs import item_detail_dialog
from db import supabase


def render() -> None:
    st.markdown(
        f'<span class="section-label">{icon_html("search",11,"#164EC6","margin-right:4px;")} Browse</span>',
        unsafe_allow_html=True,
    )
    st.title("Campus Board")
    st.caption(
        "Only admin-approved items are shown here. "
        "Found items: click Submit a Claim if you're the owner. "
        "Lost items: click I Found This if you've seen it."
    )
    st.markdown("---")

    # ── Safe Session Fallbacks ────────────────────────────────────────────────
    if "last_filter_key" not in st.session_state:
        st.session_state.last_filter_key = ""
    if "browse_page" not in st.session_state:
        st.session_state.browse_page = 0
    if "claiming_item_id" not in st.session_state:
        st.session_state.claiming_item_id = None
    if "found_report_for_id" not in st.session_state:
        st.session_state.found_report_for_id = None

    # ── Filters ───────────────────────────────────────────────────────────────
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        query = st.text_input("", placeholder="Search by item, category, or location…", label_visibility="collapsed")
    with col_filter:
        status_filter = st.selectbox("", ["All", "Lost", "Found", "Claimed"], label_visibility="collapsed")

    # Fetch live data from Supabase
    try:
        items_resp = supabase.table("items").select("*").execute()
        db_items = items_resp.data if items_resp.data else []
    except Exception as e:
        st.error(f"Error loading system items: {e}")
        db_items = []

    approved_items = [it for it in db_items if it.get("approved", False)]
    categories     = sorted({it["category"] for it in approved_items if it.get("category")}) if approved_items else []
    selected_cats  = st.multiselect("Filter by category", categories, default=[]) if categories else []
    sort_by        = st.selectbox("Sort by", ["Newest first", "Oldest first", "Lost only", "Found only"])

    # Reset pagination when filters change
    filter_key = f"{query}|{status_filter}|{','.join(selected_cats)}|{sort_by}"
    if st.session_state.last_filter_key != filter_key:
        st.session_state.browse_page     = 0
        st.session_state.last_filter_key = filter_key

    # ── Apply filters ─────────────────────────────────────────────────────────
    results = []
    for it in approved_items:
        if status_filter != "All" and it["status"] != status_filter.lower():
            continue
        if selected_cats and it["category"] not in selected_cats:
            continue
        if query:
            haystack = (it["title"] + (it["category"] or "") + (it["location"] or "") + (it["description"] or "")).lower()
            if query.lower() not in haystack:
                continue
        results.append(it)

    if sort_by == "Oldest first":
        results = list(reversed(results))
    elif sort_by == "Lost only":
        results = [r for r in results if r["status"] == "lost"]
    elif sort_by == "Found only":
        results = [r for r in results if r["status"] == "found"]

    st.caption(f"Showing {len(results)} approved item(s)")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── "I Found This" inline panel ───────────────────────────────────────────
    found_report_id = st.session_state.found_report_for_id
    if found_report_id:
        target = next((it for it in approved_items if it["id"] == found_report_id), None)
        if target:
            st.markdown(f"""
            <div class="found-panel" style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:14px; padding:1.2rem; margin-bottom:1.2rem;">
              <div style="display:flex;align-items:center;gap:6px;font-size:.68rem;font-weight:700;
                          text-transform:uppercase;letter-spacing:.1em;color:#166534;margin-bottom:.5rem;">
                {icon("box", 12, "#166534")} Reporting That You Found This Item
              </div>
              <div style="font-weight:700;font-size:1.05rem;color:#111827;">{target['title']}</div>
              <div style="display:flex;align-items:center;gap:8px;font-size:.8rem;color:#166534;margin-top:4px;">
                {badge(target['status'])} <span style="font-size: 11px; color: #6B7280;">UUID Attached</span>
                {icon_html("map-pin",12,"#166534")} {target['location']}
              </div>
            </div>
            """, unsafe_allow_html=True)

            found_proof_photo = st.file_uploader(
                "Photo of the item you found (optional)",
                type=["jpg", "jpeg", "png"],
                key=f"found_photo_{found_report_id}",
            )
            if found_proof_photo:
                preview_bytes = resize_image(found_proof_photo)
                st.markdown(photo_html(preview_bytes, width="220px", height="160px"), unsafe_allow_html=True)

            with st.form(f"found_form_{found_report_id}", clear_on_submit=True):
                st.markdown("##### Where & When Did You Find It?")
                found_location  = st.text_input("Location where you found it", placeholder="e.g. Library 2nd floor, near Rm 204", value=target["location"])
                found_date      = st.date_input("Date you found it", value=date.today())
                found_condition = st.selectbox("Item condition", ["Intact / undamaged", "Slightly damaged", "Damaged", "Unsure"])
                found_where_now = st.text_input("Where is the item now?", placeholder="e.g. Guard station, Dean's office…")
                found_notes     = st.text_area("Additional details", placeholder="Describe any marks or structural traits.", height=100)
                fc1, fc2        = st.columns(2)
                submitted_found = fc1.form_submit_button("Submit Found Report", type="primary", use_container_width=True)
                cancelled_found = fc2.form_submit_button("Cancel", use_container_width=True)

            if cancelled_found:
                st.session_state.found_report_for_id = None
                st.rerun()

            if submitted_found:
                if not found_where_now.strip():
                    st.error("Please tell us where the item is currently located.")
                else:
                    photo_str = None
                    if found_proof_photo:
                        photo_bytes = resize_image(found_proof_photo)
                        photo_str = base64.b64encode(photo_bytes).decode('utf-8')

                    note_text = f"Condition: {found_condition}. Status details: {found_where_now}. " + (found_notes.strip() or "")

                    new_found_record = {
                        "status": "found",
                        "title": target["title"],
                        "category": target["category"],
                        "location": found_location.strip() or target["location"],
                        "incident_date": found_date.strftime("%b %d"),
                        "description": note_text,
                        "contact": st.session_state.current_user["email"],
                        "reporter_email": st.session_state.current_user["email"],
                        "photo_url": photo_str,
                        "approved": False
                    }

                    try:
                        supabase.table("items").insert(new_found_record).execute()

                        # Notify the original lost item reporter
                        reporter_email = target.get("reporter_email") or target.get("contact")
                        if reporter_email:
                            finder_name = st.session_state.current_user.get("name", "Someone")
                            supabase.table("notifications").insert({
                                "user_email": reporter_email,
                                "message": f"📍 Good news! {finder_name} reported finding your lost item \"{target['title']}\" at {found_where_now}. A coordinator will review the report shortly.",
                                "is_read": False,
                            }).execute()

                        st.session_state.found_report_for_id = None
                        st.success("Found report successfully logged for coordinator approval!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to submit found report: {e}")

    st.markdown("---")

    # ── Claim panel ───────────────────────────────────────────────────────────
    claim_id = st.session_state.claiming_item_id
    if claim_id:
        target = next((it for it in approved_items if it["id"] == claim_id), None)
        if target:
            st.markdown(f"""
            <div style="background:var(--blue-light);border:1px solid #BFDBFE;border-radius:var(--radius-lg); padding:1.4rem;margin-bottom:1.5rem;">
              <h5 style="color:var(--blue);margin:0 0 .5rem 0;">Submit Claim Request</h5>
              <p style="font-size:.84rem;margin:0 0 1rem 0;">You are claiming item: <strong>{target['title']}</strong></p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("claim_form"):
                claim_proof = st.text_area("Ownership Proof Description", placeholder="Describe unique features or specify the exact date/time you lost it.")
                cc1, cc2 = st.columns(2)
                submitted_claim = cc1.form_submit_button("Submit Claim Verification", type="primary", use_container_width=True)
                cancelled_claim = cc2.form_submit_button("Cancel Claim", use_container_width=True)

            if cancelled_claim:
                st.session_state.claiming_item_id = None
                st.rerun()

            if submitted_claim:
                if not claim_proof.strip():
                    st.error("Please provide information to prove ownership.")
                else:
                    new_claim = {
                        "item_id": target["id"],
                        "claimant_email": st.session_state.current_user["email"],
                        "proof_description": claim_proof.strip(),
                        "status": "pending"
                    }
                    try:
                        supabase.table("claims").insert(new_claim).execute()
                        st.session_state.claiming_item_id = None
                        st.success("Claim request successfully logged! Faculty coordinators will review your proof.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed logging claim row: {e}")

    # ── Main Grid Layout ──────────────────────────────────────────────────────
    if not results:
        st.info("No matching items found on the board.")
        return

    start_idx = st.session_state.browse_page * ITEMS_PER_PAGE
    end_idx   = start_idx + ITEMS_PER_PAGE
    page_items = results[start_idx:end_idx]

    cols = st.columns(3)
    for index, item in enumerate(page_items):
        with cols[index % 3]:
            # Decode photo first
            photo_bytes = None
            if item.get("photo_url"):
                try:
                    photo_bytes = base64.b64decode(item["photo_url"])
                except Exception:
                    photo_bytes = None

            # Show photo or grey placeholder
            if photo_bytes:
                st.markdown(photo_html(photo_bytes, width="100%", height="160px", radius="12px 12px 0 0"), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="width:100%;height:160px;background:#F3F4F6;border-radius:12px 12px 0 0;
                            display:flex;align-items:center;justify-content:center;
                            color:#9CA3AF;font-size:.78rem;">
                  No photo
                </div>""", unsafe_allow_html=True)

            # Card info below photo
            st.markdown(f"""
            <div style="background:white; border:1px solid var(--border); border-top:none;
                        border-radius:0 0 var(--radius-lg) var(--radius-lg);
                        padding:1rem; margin-bottom:1.2rem; box-shadow:var(--shadow-sm);">
               <div style="margin-bottom:6px;">{badge(item['status'])}</div>
               <h4 style="margin:4px 0; color:var(--text);">{truncate(item['title'], 28)}</h4>
               <p style="font-size:.78rem; color:var(--text-secondary); margin:4px 0;">
                 {icon_html('map-pin',12,'#6B7280')} {item['location'] or 'No Location'}
               </p>
            </div>
            """, unsafe_allow_html=True)

            b1, b2 = st.columns(2)

            # Map DB columns to dialog-compatible keys
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

            if b1.button("View Details", key=f"det_{item['id']}", use_container_width=True):
                item_detail_dialog(compat_item)

            if item["status"] != "claimed":
                if item["status"] == "found":
                    if b2.button("Claim Item", key=f"claim_{item['id']}", type="primary", use_container_width=True):
                        st.session_state.claiming_item_id = item["id"]
                        st.rerun()
                elif item["status"] == "lost":
                    if b2.button("I Found This", key=f"ifound_{item['id']}", type="primary", use_container_width=True):
                        st.session_state.found_report_for_id = item["id"]
                        st.rerun()

    # Pagination navigation panel
    total_pages = (len(results) - 1) // ITEMS_PER_PAGE + 1
    if total_pages > 1:
        st.markdown("---")
        p_c1, p_c2, p_c3 = st.columns([1, 2, 1])
        if st.session_state.browse_page > 0:
            if p_c1.button("← Previous Page"):
                st.session_state.browse_page -= 1
                st.rerun()
        if st.session_state.browse_page < total_pages - 1:
            if p_c3.button("Next Page →"):
                st.session_state.browse_page += 1
                st.rerun()