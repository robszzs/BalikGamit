"""
sidebar.py — Sidebar navigation for BalikGamit (Supabase Connected Schema compatible).
"""

import streamlit as st
from utils import icon, icon_html
from state import is_faculty
from db import supabase
from dialogs import sign_out_confirm_dialog


def ask_groq(messages: list) -> str:
    """Send messages to Groq and return the assistant's reply."""
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I couldn't process that. ({e})"


SYSTEM_PROMPT = """You are BalikGamit Assistant, a helpful AI for RTU's Campus Lost & Found system.
You help students and faculty with questions about:
- How to report lost or found items
- How to claim an item
- How the approval process works
- How notifications work
- General tips for recovering lost items on campus

Keep answers short, friendly, and helpful. If asked something unrelated to lost and found or the app, politely redirect them.
The app is called BalikGamit and is used at Rizal Technological University (RTU)."""


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

        # ── Fetch unread notifications for current user ────────────────────
        try:
            notif_resp = supabase.table("notifications") \
                .select("*") \
                .eq("user_email", user["email"]) \
                .eq("is_read", False) \
                .order("created_at", desc=True) \
                .execute()
            unread_notifs = notif_resp.data if notif_resp.data else []
        except Exception:
            unread_notifs = []

        unread_count = len(unread_notifs)

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

        # ── Notifications bell ─────────────────────────────────────────────
        if unread_count > 0:
            st.markdown(
                f"""<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:10px;
                               padding:10px 12px;margin-bottom:16px;">
                      <div style="display:flex;align-items:center;gap:6px;font-weight:700;
                                  font-size:.8rem;color:#92400E;margin-bottom:6px;">
                        🔔 {unread_count} New Notification{"s" if unread_count > 1 else ""}
                      </div>""",
                unsafe_allow_html=True,
            )
            for notif in unread_notifs:
                st.markdown(
                    f"""<div style="font-size:.75rem;color:#374151;padding:5px 0;
                                   border-bottom:1px solid #FDE68A;line-height:1.4;">
                          {notif['message']}
                        </div>""",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("Mark all as read", use_container_width=True):
                ids = [n["id"] for n in unread_notifs]
                for nid in ids:
                    supabase.table("notifications").update({"is_read": True}).eq("id", nid).execute()
                st.rerun()

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # ── Navigation ─────────────────────────────────────────────────────
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
            sign_out_confirm_dialog()

        # ── AI Chat Assistant ──────────────────────────────────────────────
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:6px;font-size:.68rem;font-weight:700;
                    text-transform:uppercase;letter-spacing:.1em;color:#164EC6;margin-bottom:8px;">
          🤖 BalikGamit Assistant
        </div>
        """, unsafe_allow_html=True)

        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat messages
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history[-4:]:  # show last 4 messages
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="background:#EEF3FF;border-radius:10px 10px 2px 10px;
                                padding:8px 10px;margin-bottom:4px;font-size:.78rem;
                                color:#111827;text-align:right;">
                      {msg['content']}
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background:#F3F4F6;border-radius:10px 10px 10px 2px;
                                padding:8px 10px;margin-bottom:4px;font-size:.78rem;
                                color:#374151;">
                      {msg['content']}
                    </div>""", unsafe_allow_html=True)

        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("", placeholder="Ask me anything...", label_visibility="collapsed")
            send_btn   = st.form_submit_button("Send", use_container_width=True)

        if send_btn and user_input.strip():
            from better_profanity import profanity
            profanity.load_censor_words()
            if profanity.contains_profanity(user_input.strip()):
                st.error("⚠️ Please keep your messages respectful.")
            else:
                st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
                messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.chat_history
                with st.spinner("Thinking..."):
                    reply = ask_groq(messages)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

        if st.session_state.chat_history:
            if st.button("Clear chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()