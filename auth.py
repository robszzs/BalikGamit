"""
auth.py — Login and registration gate for BalikGamit (Supabase Version).
"""

import streamlit as st
from utils import icon, EMAIL_PATTERN, _hash
from db import supabase 

def render_auth_gate() -> None:
    """Render the full-page login/register UI and stop execution."""
    
    # Initialize auth_tab if it doesn't exist to prevent KeyErrors
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "login"

    _, centre, _ = st.columns([1, 2, 1])
    with centre:
        st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

        # ── Logo & Header ───────────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:32px;">
          <div style="width:52px;height:52px;background:#164EC6;border-radius:13px;
                      display:inline-flex;align-items:center;justify-content:center;
                      box-shadow:0 4px 14px rgba(22,78,198,.35);margin-bottom:12px;">
            {icon("search", 24, "white")}
          </div>
          <div style="font-weight:700;font-size:1.5rem;letter-spacing:-.04em;color:#111827;">
            BalikGamit
          </div>
          <div style="font-size:.78rem;color:#6B7280;margin-top:3px;letter-spacing:.01em;">
            Rizal Technological University &mdash; Campus Lost &amp; Found
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Custom Tabs ───────────────────────────────────────────────────────
        col1, col2 = st.columns(2)
        if col1.button("Log In", use_container_width=True, type="primary" if st.session_state.auth_tab == "login" else "secondary"):
            st.session_state.auth_tab = "login"
            st.rerun()
        if col2.button("Create Account", use_container_width=True, type="primary" if st.session_state.auth_tab == "register" else "secondary"):
            st.session_state.auth_tab = "register"
            st.rerun()

        if st.session_state.get("reg_success"):
            st.success(st.session_state.reg_success)
            st.session_state.reg_success = None

        # ── Login Logic ───────────────────────────────────────────────────────
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
                        # 1. Query Supabase for the user
                        response = supabase.table("users").select("*").eq("email", email_lc).execute()
                        
                        if not response.data:
                            st.error("No account found. Please register first.")
                        else:
                            user_data = response.data[0]
                            # 2. Check hashed password
                            if user_data["pw_hash"] != _hash(login_pw):
                                st.error("Incorrect password.")
                            else:
                                # 3. Success! Set session state
                                st.session_state.logged_in = True
                                st.session_state.current_user = {
                                    "email": email_lc, 
                                    "name": user_data["name"], 
                                    "role": user_data["role"]
                                }
                                st.session_state.page = "Home"
                                st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")

        # ── Register Logic ────────────────────────────────────────────────────
        else:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.caption("Only @rtu.edu.ph emails are accepted.")
            with st.form("reg_form"):
                reg_name  = st.text_input("Full Name", placeholder="e.g. Juan dela Cruz")
                reg_email = st.text_input("RTU Email", placeholder="0000-000000@rtu.edu.ph")
                reg_role  = st.selectbox("Role", ["Student", "Faculty"])
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
                        # 1. Check if email already exists
                        check = supabase.table("users").select("email").eq("email", email_lc).execute()
                        if check.data:
                            st.error("An account with that email already exists.")
                        else:
                            # 2. Insert the new user
                            new_user = {
                                "email": email_lc,
                                "name": reg_name.strip(),
                                "role": reg_role.lower(),
                                "pw_hash": _hash(reg_pw),
                                "status": "active"
                            }
                            supabase.table("users").insert(new_user).execute()
                            
                            st.session_state.reg_success = f"Account created! You can now sign in as {reg_name.strip()}."
                            st.session_state.auth_tab = "login"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Registration error: {e}")

    st.stop()