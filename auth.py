"""
auth.py — Login and registration gate for BalikGamit (Supabase Version).
"""

import streamlit as st
from utils import icon, EMAIL_PATTERN, _hash
from db import supabase


# ── Decorative right panel ────────────────────────────────────────────────────
SIDE_PANEL_HTML = """
<style>
  /* Hide Streamlit chrome on auth page */
  #MainMenu, footer, header { visibility: hidden; }

  /* Full-height two-column layout */
  [data-testid="stMain"] > div:first-child { padding: 0 !important; }

  .auth-wrapper {
    display: flex;
    min-height: 100vh;
    width: 100%;
  }

  /* ── Left form column ── */
  .auth-left {
    flex: 0 0 480px;
    max-width: 480px;
    padding: 56px 64px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: #ffffff;
  }

  .auth-logo-box {
    width: 48px; height: 48px;
    background: #164EC6;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 14px rgba(22,78,198,.35);
    margin-bottom: 12px;
  }

  .auth-title   { font-size: 1.6rem; font-weight: 700; color: #111827; letter-spacing: -.04em; margin: 0; }
  .auth-subtitle{ font-size: .78rem; color: #6B7280; margin: 3px 0 32px; }

  /* ── Right decorative column ── */
  .auth-right {
    flex: 1;
    background: linear-gradient(145deg, #1a3fa8 0%, #164EC6 40%, #4f6fd4 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px;
    position: relative;
    overflow: hidden;
  }

  .auth-right::before {
    content: '';
    position: absolute;
    width: 420px; height: 420px;
    background: rgba(255,255,255,.05);
    border-radius: 50%;
    top: -100px; right: -100px;
  }
  .auth-right::after {
    content: '';
    position: absolute;
    width: 300px; height: 300px;
    background: rgba(255,255,255,.05);
    border-radius: 50%;
    bottom: -80px; left: -80px;
  }

  .auth-right-title {
    font-size: 1.8rem; font-weight: 700;
    color: #ffffff;
    text-align: center;
    margin-top: 32px; margin-bottom: 12px;
    position: relative; z-index: 1;
  }
  .auth-right-sub {
    font-size: .9rem; color: rgba(255,255,255,.75);
    text-align: center; max-width: 320px;
    line-height: 1.6;
    position: relative; z-index: 1;
  }

  .auth-pill {
    background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.25);
    border-radius: 50px;
    padding: 6px 16px;
    font-size: .75rem; font-weight: 600;
    color: #ffffff;
    letter-spacing: .06em;
    text-transform: uppercase;
    margin-bottom: 20px;
    position: relative; z-index: 1;
  }

  /* Tab buttons */
  .auth-tabs { display: flex; gap: 8px; margin-bottom: 24px; }
</style>

<div class="auth-right">
  <div class="auth-pill">RTU Campus System</div>

  <svg width="280" height="240" viewBox="0 0 280 240" fill="none" xmlns="http://www.w3.org/2000/svg" style="position:relative;z-index:1;">
    <!-- Backpack body -->
    <rect x="80" y="80" width="120" height="130" rx="18" fill="white" fill-opacity="0.15" stroke="white" stroke-opacity="0.6" stroke-width="2"/>
    <!-- Backpack top handle -->
    <path d="M115 80 Q140 60 165 80" stroke="white" stroke-opacity="0.7" stroke-width="3" fill="none" stroke-linecap="round"/>
    <!-- Backpack pocket -->
    <rect x="95" y="130" width="90" height="55" rx="10" fill="white" fill-opacity="0.1" stroke="white" stroke-opacity="0.5" stroke-width="1.5"/>
    <!-- Pocket zipper -->
    <line x1="105" y1="155" x2="175" y2="155" stroke="white" stroke-opacity="0.6" stroke-width="2" stroke-linecap="round"/>
    <circle cx="140" cy="155" r="4" fill="white" fill-opacity="0.8"/>
    <!-- Straps -->
    <path d="M100 90 L88 195" stroke="white" stroke-opacity="0.5" stroke-width="4" stroke-linecap="round"/>
    <path d="M180 90 L192 195" stroke="white" stroke-opacity="0.5" stroke-width="4" stroke-linecap="round"/>
    <!-- Floating search icon -->
    <circle cx="210" cy="70" r="28" fill="white" fill-opacity="0.12" stroke="white" stroke-opacity="0.4" stroke-width="1.5"/>
    <circle cx="208" cy="67" r="10" stroke="white" stroke-opacity="0.9" stroke-width="2.5" fill="none"/>
    <line x1="215" y1="75" x2="222" y2="82" stroke="white" stroke-opacity="0.9" stroke-width="2.5" stroke-linecap="round"/>
    <!-- Floating tag -->
    <rect x="30" y="100" width="52" height="32" rx="8" fill="white" fill-opacity="0.12" stroke="white" stroke-opacity="0.4" stroke-width="1.5"/>
    <circle cx="42" cy="107" r="4" fill="white" fill-opacity="0.7"/>
    <line x1="50" y1="107" x2="72" y2="107" stroke="white" stroke-opacity="0.6" stroke-width="2" stroke-linecap="round"/>
    <line x1="42" y1="118" x2="72" y2="118" stroke="white" stroke-opacity="0.4" stroke-width="1.5" stroke-linecap="round"/>
    <!-- Sparkles -->
    <circle cx="60" cy="55"  r="3" fill="white" fill-opacity="0.5"/>
    <circle cx="220" cy="140" r="2" fill="white" fill-opacity="0.4"/>
    <circle cx="45" cy="160" r="2.5" fill="white" fill-opacity="0.35"/>
    <circle cx="230" cy="190" r="3.5" fill="white" fill-opacity="0.3"/>
    <!-- Location pin -->
    <path d="M190 38 C190 30 200 24 210 30 C218 35 218 46 210 54 L205 62 L200 54 C193 46 190 42 190 38 Z" fill="white" fill-opacity="0.25" stroke="white" stroke-opacity="0.5" stroke-width="1.5"/>
    <circle cx="204" cy="39" r="4" fill="white" fill-opacity="0.7"/>
  </svg>

  <div class="auth-right-title">Find What's Lost</div>
  <div class="auth-right-sub">BalikGamit connects RTU students and faculty to recover lost belongings across campus.</div>
</div>
"""


def render_auth_gate() -> None:
    """Render the full-page login/register UI and stop execution."""

    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "login"

    # Inject the right panel as a fixed overlay using columns trick
    left_col, right_col = st.columns([5, 6])

    with right_col:
        st.markdown(SIDE_PANEL_HTML, unsafe_allow_html=True)

    with left_col:
        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

        # ── Logo & Header ─────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="margin-bottom:28px;">
          <div style="width:48px;height:48px;background:#164EC6;border-radius:12px;
                      display:inline-flex;align-items:center;justify-content:center;
                      box-shadow:0 4px 14px rgba(22,78,198,.35);margin-bottom:12px;">
            {icon("search", 22, "white")}
          </div>
          <div style="font-size:1.6rem;font-weight:700;letter-spacing:-.04em;color:#111827;line-height:1.2;">
            {"Welcome back" if st.session_state.auth_tab == "login" else "Create account"}
          </div>
          <div style="font-size:.82rem;color:#6B7280;margin-top:4px;">
            {"Sign in to your RTU account" if st.session_state.auth_tab == "login" else "Only @rtu.edu.ph emails are accepted"}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tab toggle ────────────────────────────────────────────────────────
        col1, col2 = st.columns(2)
        if col1.button("Log In", use_container_width=True,
                       type="primary" if st.session_state.auth_tab == "login" else "secondary"):
            st.session_state.auth_tab = "login"
            st.rerun()
        if col2.button("Create Account", use_container_width=True,
                       type="primary" if st.session_state.auth_tab == "register" else "secondary"):
            st.session_state.auth_tab = "register"
            st.rerun()

        if st.session_state.get("reg_success"):
            st.success(st.session_state.reg_success)
            st.session_state.reg_success = None

        # ── Login ─────────────────────────────────────────────────────────────
        if st.session_state.auth_tab == "login":
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                login_email = st.text_input("RTU Email", placeholder="0000-000000@rtu.edu.ph")
                login_pw    = st.text_input("Password", type="password")
                login_btn   = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if login_btn:
                email_lc = login_email.strip().lower()
                if not EMAIL_PATTERN.match(email_lc):
                    st.error("Invalid email format.")
                else:
                    try:
                        response = supabase.table("users").select("*").eq("email", email_lc).execute()
                        if not response.data:
                            st.error("No account found. Please register first.")
                        else:
                            user_data = response.data[0]
                            if user_data["pw_hash"] != _hash(login_pw):
                                st.error("Incorrect password.")
                            else:
                                st.session_state.logged_in = True
                                st.session_state.current_user = {
                                    "email": email_lc,
                                    "name":  user_data["name"],
                                    "role":  user_data["role"]
                                }
                                st.session_state.page = "Home"
                                st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")

        # ── Register ──────────────────────────────────────────────────────────
        else:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            with st.form("reg_form"):
                reg_name  = st.text_input("Full Name", placeholder="e.g. Juan dela Cruz")
                reg_email = st.text_input("RTU Email", placeholder="0000-000000@rtu.edu.ph")
                reg_role  = st.selectbox("Role", ["Student"])
                reg_pw    = st.text_input("Password", type="password")
                reg_pw2   = st.text_input("Confirm Password", type="password")
                reg_btn   = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if reg_btn:
                email_lc = reg_email.strip().lower()
                if not reg_name.strip():
                    st.error("Please enter your full name.")
                elif not EMAIL_PATTERN.match(email_lc):
                    st.error("Email must be in XXXX-XXXXXX@rtu.edu.ph format.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif reg_pw != reg_pw2:
                    st.error("Passwords do not match.")
                else:
                    try:
                        check = supabase.table("users").select("email").eq("email", email_lc).execute()
                        if check.data:
                            st.error("An account with that email already exists.")
                        else:
                            supabase.table("users").insert({
                                "email":   email_lc,
                                "name":    reg_name.strip(),
                                "role":    reg_role.lower(),
                                "pw_hash": _hash(reg_pw),
                                "status":  "active"
                            }).execute()
                            st.session_state.reg_success = f"Account created! You can now sign in as {reg_name.strip()}."
                            st.session_state.auth_tab = "login"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Registration error: {e}")

    st.stop()
