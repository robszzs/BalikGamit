"""
auth.py — Login and registration gate for BalikGamit (Supabase Version).
"""

import streamlit as st
import base64
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils import icon, EMAIL_PATTERN, _hash
from db import supabase
from state import save_session_cookie


def _img_b64(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "assets", filename)
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def send_verification_email(to_email: str, code: str) -> bool:
    """Send a 6-digit verification code to the given email."""
    try:
        gmail_user     = st.secrets["GMAIL_USER"]
        gmail_password = st.secrets["GMAIL_APP_PASSWORD"]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "BalikGamit — Verify your account"
        msg["From"]    = gmail_user
        msg["To"]      = to_email

        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px 24px;
                    background:#f9fafb;border-radius:12px;border:1px solid #e2e6ea;">
          <div style="font-size:1.4rem;font-weight:800;color:#164EC6;margin-bottom:8px;">BalikGamit</div>
          <div style="font-size:.85rem;color:#6B7280;margin-bottom:24px;">Rizal Technological University — Campus Lost & Found</div>
          <div style="font-size:1rem;color:#111827;margin-bottom:16px;">Here is your verification code:</div>
          <div style="font-size:2.5rem;font-weight:800;letter-spacing:.2em;color:#164EC6;
                      background:white;border:2px solid #BFDBFE;border-radius:10px;
                      padding:16px;text-align:center;margin-bottom:16px;">
            {code}
          </div>
          <div style="font-size:.82rem;color:#6B7280;">This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</div>
        </div>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False


def render_auth_gate() -> None:
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "login"

    # Verification state
    if "pending_verification" not in st.session_state:
        st.session_state.pending_verification = None  # stores reg data while waiting for code
    if "verification_code" not in st.session_state:
        st.session_state.verification_code = None
    if "code_sent_at" not in st.session_state:
        st.session_state.code_sent_at = None

    logo_b64   = _img_b64("rtulogo.png")
    campus_b64 = _img_b64("rtumaincampus.png")

    left_col, right_col = st.columns([5, 6])

    with right_col:
        st.markdown(f"""
        <style>
          [data-testid="stMain"] > div:first-child {{ padding-top: 0 !important; }}
        </style>
        <div style="position:relative;height:100vh;min-height:500px;overflow:hidden;">
          <img src="data:image/png;base64,{campus_b64}"
               style="width:100%;height:100%;object-fit:cover;display:block;" />
          <div style="position:absolute;inset:0;background:linear-gradient(to bottom,
               rgba(22,48,120,0.45) 0%, rgba(22,48,120,0.25) 50%, rgba(10,25,80,0.75) 100%);">
          </div>
          <div style="position:absolute;bottom:48px;left:40px;right:40px;">
            <div style="font-size:2rem;font-weight:800;color:#ffffff;
                        letter-spacing:-.03em;margin-bottom:10px;
                        text-shadow:0 2px 12px rgba(0,0,0,.4);">
              BalikGamit
            </div>
            <div style="font-size:.95rem;color:rgba(255,255,255,.85);
                        line-height:1.6;max-width:380px;
                        text-shadow:0 1px 6px rgba(0,0,0,.3);">
              BalikGamit is RTU's web-based Lost &amp; Found platform — connecting students and faculty to report, search, and
              reclaim lost belongings in one organized place.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with left_col:
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:36px;">
          <img src="data:image/png;base64,{logo_b64}"
               style="width:52px;height:52px;object-fit:contain;" />
          <div>
            <div style="font-weight:700;font-size:1.1rem;color:#111827;letter-spacing:-.02em;line-height:1.2;">
              BalikGamit
            </div>
            <div style="font-size:.72rem;color:#6B7280;">Rizal Technological University</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Verification screen ───────────────────────────────────────────────
        if st.session_state.pending_verification:
            pv = st.session_state.pending_verification
            st.markdown(f"""
            <div style="margin-bottom:24px;">
              <div style="font-size:1.8rem;font-weight:800;color:#111827;letter-spacing:-.04em;line-height:1.2;">
                Check your email
              </div>
              <div style="font-size:.82rem;color:#6B7280;margin-top:6px;">
                We sent a 6-digit code to <strong>{pv['email']}</strong>
              </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("verify_form"):
                entered_code = st.text_input("Verification Code", placeholder="Enter 6-digit code", max_chars=6)
                verify_btn   = st.form_submit_button("Verify & Create Account", type="primary", use_container_width=True)

            if verify_btn:
                import time
                elapsed = time.time() - st.session_state.code_sent_at
                if elapsed > 600:
                    st.error("Code expired. Please register again.")
                    st.session_state.pending_verification = None
                    st.session_state.verification_code = None
                    st.rerun()
                elif entered_code.strip() != st.session_state.verification_code:
                    st.error("Incorrect code. Please try again.")
                else:
                    # Code is correct — create the account
                    try:
                        supabase.table("users").insert({
                            "email":   pv["email"],
                            "name":    pv["name"],
                            "role":    "student",
                            "pw_hash": _hash(pv["password"]),
                            "status":  "active"
                        }).execute()
                        st.session_state.pending_verification = None
                        st.session_state.verification_code    = None
                        st.session_state.reg_success = f"Account created! You can now sign in as {pv['name']}."
                        st.session_state.auth_tab = "login"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Registration error: {e}")

            if st.button("← Back to registration", use_container_width=True):
                st.session_state.pending_verification = None
                st.session_state.verification_code    = None
                st.rerun()

            st.stop()

        # ── Normal tabs ───────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="margin-bottom:28px;">
          <div style="font-size:1.8rem;font-weight:800;color:#111827;letter-spacing:-.04em;line-height:1.2;">
            {"Welcome back" if st.session_state.auth_tab == "login" else "Create account"}
          </div>
          <div style="font-size:.82rem;color:#6B7280;margin-top:6px;">
            {"Please enter your details to sign in." if st.session_state.auth_tab == "login" else "Only @rtu.edu.ph emails are accepted."}
          </div>
        </div>
        """, unsafe_allow_html=True)

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
                                user = {
                                    "email": email_lc,
                                    "name":  user_data["name"],
                                    "role":  user_data["role"]
                                }
                                st.session_state.logged_in    = True
                                st.session_state.current_user = user
                                st.session_state.page         = "Home"
                                save_session_cookie(user)
                                st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")

        else:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            with st.form("reg_form"):
                reg_name  = st.text_input("Full Name", placeholder="e.g. Juan dela Cruz")
                reg_email = st.text_input("RTU Email", placeholder="0000-000000@rtu.edu.ph")
                reg_pw    = st.text_input("Password", type="password")
                reg_pw2   = st.text_input("Confirm Password", type="password")
                reg_btn   = st.form_submit_button("Send Verification Code", type="primary", use_container_width=True)

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
                            # Generate and send verification code
                            code = str(random.randint(100000, 999999))
                            with st.spinner("Sending verification code to your email..."):
                                sent = send_verification_email(email_lc, code)
                            if sent:
                                import time
                                st.session_state.verification_code    = code
                                st.session_state.code_sent_at         = time.time()
                                st.session_state.pending_verification = {
                                    "email":    email_lc,
                                    "name":     reg_name.strip(),
                                    "password": reg_pw,
                                }
                                st.rerun()
                    except Exception as e:
                        st.error(f"Registration error: {e}")

    st.stop()