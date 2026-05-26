"""
pages/home.py — Home page for BalikGamit (Supabase Connected).
"""

import streamlit as st
import base64
from utils import icon, icon_html, badge, photo_html, truncate, CATEGORY_ICONS
from dialogs import item_detail_dialog
from db import supabase

STATUS_COLORS = {
    "lost":    {"bg": "#FEF2F2", "border": "#FECACA", "accent": "#EF4444", "icon": "🔴"},
    "found":   {"bg": "#EFF6FF", "border": "#BFDBFE", "accent": "#3B82F6", "icon": "🔵"},
    "claimed": {"bg": "#F0FDF4", "border": "#BBF7D0", "accent": "#22C55E", "icon": "🟢"},
}

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

    # ── My Claims ─────────────────────────────────────────────────────────────
    current_email = st.session_state.current_user["email"]
    try:
        my_claims_resp = supabase.table("claims").select("*").eq("claimant_email", current_email).execute()
        my_claims = my_claims_resp.data if my_claims_resp.data else []
    except Exception:
        my_claims = []

    if my_claims:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<span class="section-label">{icon_html("clipboard",11,"#164EC6","margin-right:4px;")} My Activity</span>',
            unsafe_allow_html=True,
        )
        st.subheader("My Claim Requests")

        for clm in my_claims:
            status = clm.get("status", "pending")
            style = {
                "pending":  ("#FFFBEB", "#FCD34D", "#92400E", "⏳"),
                "approved": ("#F0FDF4", "#BBF7D0", "#166534", "✅"),
                "rejected": ("#FEF2F2", "#FECACA", "#991B1B", "❌"),
            }.get(status, ("#F9FAFB", "#E5E7EB", "#374151", "•"))

            try:
                item_resp = supabase.table("items").select("title, location").eq("id", clm["item_id"]).execute()
                item_info = item_resp.data[0] if item_resp.data else {}
            except Exception:
                item_info = {}

            proof_snippet = clm.get("proof_description", "—")
            proof_snippet = proof_snippet[:80] + "..." if len(proof_snippet) > 80 else proof_snippet

            st.markdown(f"""
            <div style="background:{style[0]};border:1px solid {style[1]};
                        border-left:4px solid {style[1]};border-radius:10px;
                        padding:12px 16px;margin-bottom:8px;
                        display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
              <div>
                <div style="font-weight:700;font-size:.88rem;color:#111827;">
                  {style[3]} {item_info.get('title', 'Unknown Item')}
                </div>
                <div style="font-size:.74rem;color:#6B7280;margin-top:3px;">
                  📍 {item_info.get('location', '—')}
                </div>
                <div style="font-size:.74rem;color:#6B7280;margin-top:2px;font-style:italic;">
                  Proof submitted: {proof_snippet}
                </div>
              </div>
              <span style="font-size:.72rem;font-weight:700;text-transform:uppercase;
                           color:{style[2]};letter-spacing:.06em;white-space:nowrap;">
                {status.upper()}
              </span>
            </div>
            """, unsafe_allow_html=True)

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
                photo_bytes = None
                if item.get("photo_url"):
                    try:
                        photo_bytes = base64.b64decode(item["photo_url"])
                    except Exception:
                        photo_bytes = None

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

                colors = STATUS_COLORS.get(item["status"], STATUS_COLORS["lost"])

                with st.container():
                    f_col1, f_col2 = st.columns([1, 4])
                    with f_col1:
                        if photo_bytes:
                            st.markdown(photo_html(photo_bytes, width="100%", height="80px", radius="10px"), unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="width:100%;height:80px;background:{colors['bg']};
                                        border:1px solid {colors['border']};border-radius:10px;
                                        display:flex;align-items:center;justify-content:center;
                                        font-size:1.5rem;">
                              {colors['icon']}
                            </div>""", unsafe_allow_html=True)
                    with f_col2:
                        st.markdown(f"""
                        <div style="background:{colors['bg']};border:1px solid {colors['border']};
                                    border-left:4px solid {colors['accent']};
                                    border-radius:10px;padding:10px 14px;margin-bottom:6px;">
                          <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                            <span style="font-weight:700;font-size:.92rem;color:#111827;">{item['title']}</span>
                            {badge(item['status'])}
                          </div>
                          <div style="font-size:.75rem;color:#6B7280;">
                            📂 {item.get('category','—')} &nbsp;·&nbsp;
                            📍 {item.get('location','—')} &nbsp;·&nbsp;
                            📅 {item.get('incident_date','—')}
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("View Details", key=f"home_view_{item['id']}"):
                            item_detail_dialog(compat_item)

    with col_nav:
        st.markdown(
            f'<span class="section-label">{icon_html("navigation",11,"#164EC6","margin-right:4px;")} Quick Navigation</span>',
            unsafe_allow_html=True,
        )
        st.subheader("Get Started")

        st.markdown("""
        <div style="background:linear-gradient(135deg,#EFF6FF,#DBEAFE);border:1px solid #BFDBFE;
                    border-radius:12px;padding:14px;margin-bottom:12px;">
          <div style="font-size:.8rem;color:#1D4ED8;font-weight:600;margin-bottom:4px;">🔍 Browse Board</div>
          <div style="font-size:.73rem;color:#3B82F6;">View all approved lost & found items on campus.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Campus Board", use_container_width=True, type="primary"):
            st.session_state.page = "Browse Items"
            st.rerun()

        st.markdown("""
        <div style="background:linear-gradient(135deg,#FFF7ED,#FFEDD5);border:1px solid #FED7AA;
                    border-radius:12px;padding:14px;margin-bottom:12px;margin-top:12px;">
          <div style="font-size:.8rem;color:#C2410C;font-weight:600;margin-bottom:4px;">📋 Report Item</div>
          <div style="font-size:.73rem;color:#EA580C;">Lost something or found an item? Post it here.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Report Lost or Found Item", use_container_width=True):
            st.session_state.page = "Post an Item"
            st.rerun()
