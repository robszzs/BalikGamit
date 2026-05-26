"""
pages/admin.py — Admin Dashboard page for BalikGamit (Supabase Connected).
"""

import streamlit as st
import base64
from utils import icon, icon_html, badge, photo_html
from state import is_faculty
from db import supabase
from dialogs import create_faculty_dialog


def send_notification(user_email: str, message: str) -> None:
    """Insert a notification row for the given user."""
    try:
        supabase.table("notifications").insert({
            "user_email": user_email,
            "message": message,
            "is_read": False,
        }).execute()
    except Exception as e:
        st.warning(f"Could not send notification: {e}")


def render() -> None:
    if not is_faculty():
        st.error("Access denied. This page is only available to faculty coordinators.")
        st.stop()

    st.markdown(
        f'<span class="section-label">{icon_html("shield",11,"#164EC6","margin-right:4px;")} Coordinator</span>',
        unsafe_allow_html=True,
    )
    st.title("Admin Dashboard")
    st.caption("Approve posts, manage claim requests, and keep the campus board accurate.")
    st.markdown("---")
    col_title, col_btn = st.columns([4, 1])
    with col_btn:
        if st.button("+ Faculty Account", type="primary", use_container_width=True):
            create_faculty_dialog()

    # ── Fetch live metrics from Supabase ──────────────────────────────────────
    try:
        items_resp = supabase.table("items").select("*").execute()
        db_items = items_resp.data if items_resp.data else []

        claims_resp = supabase.table("claims").select("*").execute()
        raw_claims = claims_resp.data if claims_resp.data else []

        users_resp = supabase.table("users").select("*").execute()
        db_users = users_resp.data if users_resp.data else []
    except Exception as e:
        st.error(f"Error communicating with backend databases: {e}")
        db_items, raw_claims, db_users = [], [], []

    # Build lookup maps for joins
    items_map = {it["id"]: it for it in db_items}
    users_map = {u["email"]: u for u in db_users}

    # Enrich claims with item title and claimant name
    db_claims = []
    for clm in raw_claims:
        item = items_map.get(clm.get("item_id"), {})
        claimant = users_map.get(clm.get("claimant_email"), {})
        db_claims.append({
            **clm,
            "item_title": item.get("title", "Unknown Item"),
            "claimant_name": claimant.get("name", clm.get("claimant_email", "Unknown")),
            "proof_text": clm.get("proof_description", ""),
        })

    pending_posts  = [it for it in db_items if not it.get("approved", False)]
    approved_items = [it for it in db_items if it.get("approved", False)]

    # ── Overview metrics ──────────────────────────────────────────────────────
    st.markdown(
        f'<span class="section-label">{icon_html("bar-chart",11,"#164EC6","margin-right:4px;")} Overview</span>',
        unsafe_allow_html=True,
    )
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Lost Reports",     str(sum(1 for i in approved_items if i["status"] == "lost")))
    k2.metric("Found Items",      str(sum(1 for i in approved_items if i["status"] == "found")))
    k3.metric("Items Returned",   str(sum(1 for i in approved_items if i["status"] == "claimed")))
    k4.metric("Pending Review",   str(len(pending_posts)))
    k5.metric("Registered Users", str(len(db_users)))

    st.markdown("<br>", unsafe_allow_html=True)

    pend_col, live_col = st.columns([2, 1])

    # ── Pending post approvals ────────────────────────────────────────────────
    with pend_col:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:.5rem;">'
            f'{icon_html("file-text",15,"#374151")}'
            f'<span style="font-weight:700;font-size:1.05rem;">Pending Post Approvals</span>'
            f'<span class="badge badge-pending">{len(pending_posts)} pending</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if not pending_posts:
            st.info("No pending posts — all clear.")
        else:
            for idx, r in enumerate(pending_posts):
                photo_bytes = None
                if r.get("photo_url"):
                    try:
                        photo_bytes = base64.b64decode(r["photo_url"])
                    except Exception:
                        photo_bytes = None

                reporter_label = users_map.get(r.get("reporter_email", ""), {}).get("name", r.get("reporter_email", "User"))
                reporter_email = r.get("reporter_email", "")

                if photo_bytes:
                    p_col, d_col = st.columns([1, 2])
                    with p_col:
                        st.markdown(photo_html(photo_bytes, width="100%", height="120px", radius="10px"), unsafe_allow_html=True)
                    with d_col:
                        st.markdown(f"**{r['title']}**")
                        st.markdown(
                            badge(r["status"]) +
                            f"<span style='font-size:.72rem;color:#9CA3AF;margin-left:8px;font-family:\"DM Mono\",monospace;'>`{r['id']}` &middot; {reporter_label}</span>",
                            unsafe_allow_html=True,
                        )
                        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                        btn_a, btn_r = st.columns(2)
                        if btn_a.button("Approve", key=f"approve_{idx}", type="primary", use_container_width=True):
                            supabase.table("items").update({"approved": True}).eq("id", r["id"]).execute()
                            send_notification(
                                reporter_email,
                                f"✅ Your post \"{r['title']}\" has been approved and is now visible on the Campus Board!"
                            )
                            st.toast(f"{r['title']} approved.", icon="✅")
                            st.rerun()
                        if btn_r.button("Reject", key=f"reject_{idx}", use_container_width=True):
                            supabase.table("items").delete().eq("id", r["id"]).execute()
                            send_notification(
                                reporter_email,
                                f"❌ Your post \"{r['title']}\" was rejected by a coordinator."
                            )
                            st.toast(f"{r['title']} rejected and removed.", icon="❌")
                            st.rerun()
                else:
                    row = st.columns([3, 1, 1, 2])
                    row[0].markdown(f"**{r['title']}** \n`{r['id']} · {reporter_label}`")
                    row[1].markdown(badge(r["status"]), unsafe_allow_html=True)
                    row[2].markdown(f"<span style='font-size:.78rem;color:#9CA3AF'>{r.get('incident_date', 'Today')}</span>", unsafe_allow_html=True)
                    c_approve, c_reject = row[3].columns(2)
                    if c_approve.button("Approve", key=f"app_txt_{idx}", type="primary", use_container_width=True):
                        supabase.table("items").update({"approved": True}).eq("id", r["id"]).execute()
                        send_notification(
                            reporter_email,
                            f"✅ Your post \"{r['title']}\" has been approved and is now visible on the Campus Board!"
                        )
                        st.toast(f"{r['title']} approved.", icon="✅")
                        st.rerun()
                    if c_reject.button("Reject", key=f"rej_txt_{idx}", use_container_width=True):
                        supabase.table("items").delete().eq("id", r["id"]).execute()
                        send_notification(
                            reporter_email,
                            f"❌ Your post \"{r['title']}\" was rejected by a coordinator."
                        )
                        st.toast(f"{r['title']} removed.", icon="❌")
                        st.rerun()

    # ── Claim Tickets panel ───────────────────────────────────────────────────
    with live_col:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:.5rem;">'
            f'{icon_html("activity",15,"#374151")}'
            f'<span style="font-weight:700;font-size:1.05rem;">Claim Tickets</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        pending_claims = [c for c in db_claims if c.get("status") == "pending"]
        if not pending_claims:
            st.info("No active claim tickets reported.")
        else:
            for c_idx, clm in enumerate(pending_claims):
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#EFF6FF,#DBEAFE);border:1px solid #BFDBFE;
                            border-left:4px solid #3B82F6;border-radius:10px;padding:12px;margin-bottom:10px;">
                  <div style="font-weight:700;font-size:.84rem;color:#1D4ED8;margin-bottom:4px;">
                    🎫 Claim on: {clm['item_title']}
                  </div>
                  <div style="font-size:.74rem;color:#3B82F6;margin-bottom:6px;">
                    👤 {clm['claimant_name']} · {clm['claimant_email']}
                  </div>
                  <div style="background:white;border:1px solid #BFDBFE;padding:8px;
                              border-radius:6px;font-size:.76rem;color:#374151;font-style:italic;">
                    \"{clm['proof_text']}\"
                  </div>
                </div>
                """, unsafe_allow_html=True)
                cb1, cb2 = st.columns(2)
                if cb1.button("Grant", key=f"grant_{c_idx}", type="primary", use_container_width=True):
                    supabase.table("claims").update({"status": "approved"}).eq("id", clm["id"]).execute()
                    supabase.table("items").update({"status": "claimed"}).eq("id", clm["item_id"]).execute()

                    # Auto-delete duplicate lost/found entries with the same title
                    original_item = items_map.get(clm.get("item_id"), {})
                    item_title = original_item.get("title", "")
                    if item_title:
                        # Delete all OTHER items with same title that are lost or found (not the claimed one)
                        duplicates_resp = supabase.table("items") \
                            .select("id") \
                            .eq("title", item_title) \
                            .neq("id", clm["item_id"]) \
                            .in_("status", ["lost", "found"]) \
                            .execute()
                        for dup in (duplicates_resp.data or []):
                            supabase.table("items").delete().eq("id", dup["id"]).execute()

                    # Notify the claimant
                    send_notification(
                        clm["claimant_email"],
                        f"🎉 Your claim on \"{clm['item_title']}\" has been approved! Please coordinate with the faculty to retrieve your item."
                    )
                    # Notify the original reporter
                    if original_item.get("reporter_email"):
                        send_notification(
                            original_item["reporter_email"],
                            f"📦 Great news! Your reported item \"{clm['item_title']}\" has been claimed and returned to its owner."
                        )
                    st.success("Item returned safely to owner!")
                    st.rerun()
                if cb2.button("Deny", key=f"deny_{c_idx}", use_container_width=True):
                    supabase.table("claims").update({"status": "rejected"}).eq("id", clm["id"]).execute()
                    send_notification(
                        clm["claimant_email"],
                        f"❌ Your claim on \"{clm['item_title']}\" was denied by a coordinator. You may submit a new claim with more proof."
                    )
                    st.toast("Claim ticket denied.")
                    st.rerun()

    # ── Claimed Items History ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:.5rem;">'
        f'{icon_html("check-circle",15,"#166534")}'
        f'<span style="font-weight:700;font-size:1.05rem;">Claimed Items History</span>'
        f'<span class="badge badge-claimed">{len([c for c in db_claims if c.get("status") == "approved"])} resolved</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    approved_claims = [c for c in db_claims if c.get("status") == "approved"]

    if not approved_claims:
        st.info("No claimed items yet.")
    else:
        for clm in approved_claims:
            original_item = items_map.get(clm.get("item_id"), {})
            st.markdown(f"""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;
                        border-left:4px solid #22C55E;border-radius:10px;
                        padding:12px 16px;margin-bottom:8px;
                        display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
              <div>
                <div style="font-weight:700;font-size:.88rem;color:#111827;">
                  ✅ {clm['item_title']}
                </div>
                <div style="font-size:.74rem;color:#6B7280;margin-top:3px;">
                  Claimed by: <strong>{clm['claimant_name']}</strong> · {clm['claimant_email']}
                </div>
                <div style="font-size:.74rem;color:#6B7280;margin-top:2px;">
                  Category: {original_item.get('category', '—')} &nbsp;·&nbsp;
                  Location: {original_item.get('location', '—')} &nbsp;·&nbsp;
                  Date reported: {original_item.get('incident_date', '—')}
                </div>
              </div>
              <span class="badge badge-claimed">RESOLVED</span>
            </div>
            """, unsafe_allow_html=True)   

                    
