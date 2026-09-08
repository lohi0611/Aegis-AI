"""
AEGIS Safety Intelligence — Split-Screen Authentication System
Asymmetric layout with branding, value propositions, and live telemetry on the left,
and clean, responsive Sign In / Sign Up tabs with password strength meter and
one-click demo login on the right.
"""

import re
import streamlit as st
from db import authenticate_user, register_user
from ui_utils import ICONS, render_theme_toggle


def check_password_strength(password: str):
    """Calculate password strength score from 0 to 100 and feedback label."""
    if not password:
        return 0, "Enter password", "#64748B"

    score = 0
    if len(password) >= 6:
        score += 25
    if len(password) >= 10:
        score += 25
    if re.search(r"\d", password):
        score += 25
    if re.search(r"[A-Z]", password) and re.search(r"[\W_]", password):
        score += 25

    if score <= 25:
        return score, "Weak", "#EF4444"
    elif score <= 50:
        return score, "Fair", "#F59E0B"
    elif score <= 75:
        return score, "Good", "#06B6D4"
    else:
        return score, "Strong & Secure", "#10B981"


def render_auth_page(initial_mode: str = "login"):
    """Render split-screen authentication page."""

    # Top return bar
    col_back, col_spacer, col_theme = st.columns([2, 8, 1])
    with col_back:
        if st.button("← Back to Overview", key="auth_back_to_landing"):
            st.session_state.active_view = "landing"
            st.rerun()
    with col_theme:
        render_theme_toggle(key="auth_theme_toggle")

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # Main split container
    col_left, col_right = st.columns([1.1, 1.3], gap="large")

    # ── LEFT BRAND / HERO COLUMN ─────────────────────────────────────────────
    with col_left:
        st.markdown(f"""
<div class="auth-left-hero" style="border-radius:16px;">
<div>
<div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
<div style="width:42px;height:42px;background:rgba(245,158,11,0.12);border:1.5px solid rgba(245,158,11,0.35);border-radius:12px;display:flex;align-items:center;justify-content:center;color:#F59E0B;flex-shrink:0;">
{ICONS['shield'].replace('18', '24')}
</div>
<div>
<div style="font-size:1.2rem;font-weight:900;letter-spacing:1px;color:var(--text-primary);">AEGIS AI</div>
<div style="font-size:0.68rem;color:var(--text-muted);letter-spacing:0.6px;text-transform:uppercase;">Safety Command</div>
</div>
</div>
<div style="font-size:1.9rem;font-weight:800;line-height:1.22;color:var(--text-primary);margin-bottom:14px;">
Next-Generation <br>
<span style="color:var(--accent);">Safety Intelligence</span>
</div>
<p style="font-size:0.88rem;color:var(--text-secondary);line-height:1.6;margin-bottom:28px;">
Join world-class engineering teams leveraging real-time neural vision to protect personnel, automate OSHA compliance, and eliminate catastrophic job site hazards.
</p>
<div style="display:flex;flex-direction:column;gap:14px;margin-bottom:30px;">
<div style="display:flex;align-items:flex-start;gap:12px;">
<div style="color:#10B981;margin-top:2px;">{ICONS['check-circle']}</div>
<div>
<div style="font-size:0.84rem;font-weight:700;color:var(--text-primary);">Sub-30ms Edge Detection</div>
<div style="font-size:0.75rem;color:var(--text-muted);">High-precision YOLOv8 model tuned for challenging worksite lighting.</div>
</div>
</div>
<div style="display:flex;align-items:flex-start;gap:12px;">
<div style="color:#F59E0B;margin-top:2px;">{ICONS['activity']}</div>
<div>
<div style="font-size:0.84rem;font-weight:700;color:var(--text-primary);">Spatial Anatomical Correlator</div>
<div style="font-size:0.75rem;color:var(--text-muted);">Accurately links safety equipment to individual worker tracks.</div>
</div>
</div>
<div style="display:flex;align-items:flex-start;gap:12px;">
<div style="color:#06B6D4;margin-top:2px;">{ICONS['database']}</div>
<div>
<div style="font-size:0.84rem;font-weight:700;color:var(--text-primary);">Cryptographic Audit Trail</div>
<div style="font-size:0.75rem;color:var(--text-muted);">Immutable incident database with full-resolution visual snapshots.</div>
</div>
</div>
</div>
</div>
<div style="background:var(--bg-card-2);border:1px solid var(--border-subtle);border-radius:10px;padding:14px;">
<div style="display:flex;justify-content:space-between;align-items:center;">
<div style="display:flex;align-items:center;gap:6px;">
<span class="dot dot-live"></span>
<span style="font-size:0.72rem;font-weight:700;color:var(--text-primary);letter-spacing:0.5px;">SYSTEM STATUS</span>
</div>
<span style="font-size:0.72rem;color:#10B981;font-weight:600;">ACTIVE</span>
</div>
<div style="display:flex;justify-content:space-between;margin-top:8px;font-size:0.75rem;color:var(--text-secondary);">
<span>Core Version: <b>v2.4.0-prod</b></span>
<span>Security: <b>PBKDF2-HMAC</b></span>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    # ── RIGHT AUTHENTICATION COLUMN ──────────────────────────────────────────
    with col_right:
        st.markdown("""
<div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:16px;padding:28px 24px;box-shadow:var(--shadow-card);">
""", unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Sign In to Workspace", "Create New Account"])

        # ── TAB 1: SIGN IN ───────────────────────────────────────────────────
        with tab_login:
            st.markdown("""
<div style="margin-bottom:18px;">
    <div style="font-size:1.3rem;font-weight:800;color:var(--text-primary);">Welcome back 👋</div>
    <div style="font-size:0.82rem;color:var(--text-secondary);">Enter your authorized credentials to access your safety dashboard.</div>
</div>
""", unsafe_allow_html=True)

            # Check for demo prefill
            default_email = "admin@aegis.ai" if st.session_state.get("demo_prefill") else ""
            default_pwd = "Admin@1234" if st.session_state.get("demo_prefill") else ""

            login_email = st.text_input("Work Email Address", value=default_email, key="login_email_input", placeholder="inspector@organization.com")

            show_pwd = st.checkbox("Show Password", key="login_show_pwd_chk")
            login_pwd = st.text_input("Password", value=default_pwd, type="default" if show_pwd else "password", key="login_pwd_input", placeholder="••••••••")

            col_rem, col_forgot = st.columns([1, 1])
            with col_rem:
                st.checkbox("Remember this workstation", value=True, key="login_remember_chk")
            with col_forgot:
                with st.expander("Forgot Password?", expanded=False):
                    st.caption("Contact your site system administrator or use the demo login credentials below.")

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

            if st.button("🔐 Sign In", key="btn_execute_login", use_container_width=True):
                if not login_email or not login_pwd:
                    st.error("Please enter both email and password.")
                else:
                    with st.spinner("Authenticating credentials..."):
                        user = authenticate_user(login_email, login_pwd)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.active_view = "dashboard"
                            st.success(f"Welcome, {user.get('full_name')}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please verify your email and password.")

            st.markdown("<div style='height:14px;border-bottom:1px solid var(--border-subtle);margin-bottom:14px;'></div>", unsafe_allow_html=True)

            # Quick Demo Login Button
            st.markdown("""
<div style="text-align:center;font-size:0.75rem;color:var(--text-muted);margin-bottom:8px;">
    FOR EVALUATION &amp; TESTING:
</div>
""", unsafe_allow_html=True)
            if st.button("⚡ One-Click Demo Login (Admin Access)", key="btn_instant_demo_login", use_container_width=True):
                user = authenticate_user("admin@aegis.ai", "Admin@1234")
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.active_view = "dashboard"
                    st.success("Authenticated as Alex Vance (Chief Safety Officer)")
                    st.rerun()
                else:
                    st.error("Default demo user initializing... please retry in a moment.")

        # ── TAB 2: SIGN UP ───────────────────────────────────────────────────
        with tab_signup:
            st.markdown("""
<div style="margin-bottom:18px;">
    <div style="font-size:1.3rem;font-weight:800;color:var(--text-primary);">Create Your Account 🚀</div>
    <div style="font-size:0.82rem;color:var(--text-secondary);">Set up instant real-time safety monitoring for your site.</div>
</div>
""", unsafe_allow_html=True)

            reg_name = st.text_input("Full Name", key="reg_name_input", placeholder="e.g. Sarah Connor")
            reg_email = st.text_input("Work Email Address", key="reg_email_input", placeholder="s.connor@constructionsite.com")

            reg_role = st.selectbox(
                "Designated Worksite Role",
                ["Safety Inspector", "Site Project Manager", "EHS Compliance Officer", "Safety Systems Engineer"],
                key="reg_role_select",
            )

            reg_pwd = st.text_input("Create Password", type="password", key="reg_pwd_input", placeholder="Minimum 6 characters")

            # Real-time Password Strength Meter
            score, label, color = check_password_strength(reg_pwd)
            if reg_pwd:
                st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;font-size:0.72rem;margin-top:2px;">
    <span style="color:var(--text-muted);">Strength:</span>
    <span style="font-weight:700;color:{color};">{label}</span>
</div>
<div class="auth-strength-bar">
    <div class="auth-strength-fill" style="width:{score}%;background:{color};"></div>
</div>
""", unsafe_allow_html=True)

            reg_pwd_confirm = st.text_input("Confirm Password", type="password", key="reg_pwd_confirm_input", placeholder="Repeat password")

            terms_accepted = st.checkbox(
                "I certify I am an authorized safety representative agreeing to safety compliance logging terms.",
                value=True,
                key="reg_terms_chk",
            )

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

            if st.button("✨ Create Account & Launch", key="btn_execute_signup", use_container_width=True):
                if not reg_name or not reg_email or not reg_pwd:
                    st.error("Please fill in all required fields.")
                elif "@" not in reg_email or "." not in reg_email:
                    st.error("Please provide a valid work email address.")
                elif len(reg_pwd) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif reg_pwd != reg_pwd_confirm:
                    st.error("Passwords do not match. Please re-enter.")
                elif not terms_accepted:
                    st.warning("You must accept the safety compliance certification.")
                else:
                    with st.spinner("Registering user in secure database..."):
                        new_user = register_user(reg_email, reg_pwd, reg_name, reg_role)
                        if new_user:
                            st.session_state.authenticated = True
                            st.session_state.user = new_user
                            st.session_state.active_view = "dashboard"
                            st.success(f"Account successfully created! Welcome, {reg_name}.")
                            st.rerun()
                        else:
                            st.error("An account with this email address already exists. Please Sign In instead.")

        st.markdown("</div>", unsafe_allow_html=True)
