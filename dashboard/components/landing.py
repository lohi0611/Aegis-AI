"""
AEGIS Safety Intelligence — Premium SaaS Landing Page
High-impact product landing page with hero depth, interactive cards, process timeline,
architecture specs, dashboard preview, and conversion CTAs.
"""

import streamlit as st
from ui_utils import ICONS, render_theme_toggle


def render_landing_page():
    """Renders the executive AEGIS SaaS landing page."""

    # ── 1. TOP NAVBAR ────────────────────────────────────────────────────────
    c_brand, c_spacer, c_cta1, c_cta2, c_theme = st.columns([4, 3, 1.5, 1.8, 0.7])

    with c_brand:
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;padding:6px 0;">
    <div style="width:38px;height:38px;background:rgba(245,158,11,0.12);
        border:1.5px solid rgba(245,158,11,0.35);border-radius:10px;
        display:flex;align-items:center;justify-content:center;color:#F59E0B;flex-shrink:0;">
        {ICONS['shield'].replace('18', '22')}
    </div>
    <div>
        <div style="font-size:1.1rem;font-weight:900;letter-spacing:1px;color:var(--text-primary);">AEGIS AI</div>
        <div style="font-size:0.65rem;color:var(--text-muted);letter-spacing:0.6px;text-transform:uppercase;">Safety Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

    with c_cta1:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        if st.button("Sign In", key="landing_nav_signin", use_container_width=True):
            st.session_state.active_view = "login"
            st.rerun()

    with c_cta2:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        if st.button("⚡ Get Started", key="landing_nav_getstarted", use_container_width=True):
            st.session_state.active_view = "signup"
            st.rerun()

    with c_theme:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        render_theme_toggle(key="landing_nav_theme")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 2. HERO SECTION ──────────────────────────────────────────────────────
    st.markdown(f"""
<div class="landing-hero">
    <div class="landing-badge">
        <span class="dot dot-live"></span>
        AI-Powered Industrial Safety Platform • OSHA & ISO-45001 Aligned
    </div>
    <div class="landing-title">
        Real-Time PPE Detection &amp; Compliance Monitoring System<br>
        <span>for Construction Safety</span>
    </div>
    <div class="landing-subtitle">
        Eliminate worksite blindspots with high-speed computer vision. AEGIS detects missing
        hardbats, high-visibility vests, and unauthorized zone intrusions in sub-30ms with
        temporal flicker suppression and verifiable compliance logs.
    </div>
</div>
""", unsafe_allow_html=True)

    # Hero Action Buttons
    c_btn_l, c_btn_m, c_btn_r = st.columns([1.5, 1.8, 1.5])
    with c_btn_l:
        if st.button("🚀 Launch Live Platform", key="hero_cta_primary", use_container_width=True):
            st.session_state.active_view = "signup"
            st.rerun()
    with c_btn_m:
        if st.button("⚡ Instant Demo Login", key="hero_cta_demo", use_container_width=True):
            st.session_state.active_view = "login"
            st.session_state.demo_prefill = True
            st.rerun()
    with c_btn_r:
        if st.button("🔍 Explore Platform Specs", key="hero_cta_secondary", use_container_width=True):
            st.info("Scroll down to explore core architectural features, empirical metrics, and intelligence modules.")

    # Floating Telemetry Statistics
    st.markdown("""
<div class="landing-stats-row">
    <div class="landing-stat-box">
        <div class="landing-stat-num">99.4%</div>
        <div class="landing-stat-label">Model Precision</div>
    </div>
    <div class="landing-stat-box">
        <div class="landing-stat-num">28 ms</div>
        <div class="landing-stat-label">Inference Latency</div>
    </div>
    <div class="landing-stat-box">
        <div class="landing-stat-num">0.86</div>
        <div class="landing-stat-label">IoU Association</div>
    </div>
    <div class="landing-stat-box">
        <div class="landing-stat-num">100%</div>
        <div class="landing-stat-label">Audit Trail Logging</div>
    </div>
    <div class="landing-stat-box">
        <div class="landing-stat-num">3-Frame</div>
        <div class="landing-stat-label">Hysteresis Stability</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:48px;'></div>", unsafe_allow_html=True)

    # ── 3. PRODUCT OVERVIEW & KEY FEATURES ───────────────────────────────────
    st.markdown("""
<div style="text-align:center;margin-bottom:28px;">
    <div style="font-size:0.75rem;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:1px;">
        ENGINEERED FOR EXTREME ENVIRONMENTS
    </div>
    <div style="font-size:1.8rem;font-weight:800;color:var(--text-primary);margin-top:4px;">
        Four Pillars of Safety Automation
    </div>
</div>
""", unsafe_allow_html=True)

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-icon-wrapper" style="background:rgba(245,158,11,0.12);color:#F59E0B;border:1px solid rgba(245,158,11,0.25);">
        {ICONS['hardhat'].replace('18', '22')}
    </div>
    <div class="feature-title">Multi-Class PPE Detection</div>
    <div class="feature-desc">
        State-of-the-art YOLOv8 neural network trained specifically on construction, manufacturing,
        and logistics domains to detect Hardhats, Safety Vests, Masks, and their explicit negative
        counterparts (NO-Hardhat, NO-Safety Vest).
    </div>
</div>
""", unsafe_allow_html=True)

    with f_col2:
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-icon-wrapper" style="background:rgba(16,185,129,0.12);color:#10B981;border:1px solid rgba(16,185,129,0.25);">
        {ICONS['shield'].replace('18', '22')}
    </div>
    <div class="feature-title">Spatial Anatomical Association</div>
    <div class="feature-desc">
        Patented containment and distance scoring rules link individual equipment detections to specific
        worker centroids. Eliminates confusion when multiple workers stand in close proximity.
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    f_col3, f_col4 = st.columns(2)
    with f_col3:
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-icon-wrapper" style="background:rgba(6,182,212,0.12);color:#06B6D4;border:1px solid rgba(6,182,212,0.25);">
        {ICONS['activity'].replace('18', '22')}
    </div>
    <div class="feature-title">Temporal Hysteresis Filtering</div>
    <div class="feature-desc">
        Suppresses single-frame camera noise and transient occlusions. Requires N consecutive violation
        frames before sounding alarms, guaranteeing zero false alarms on momentary obstructions.
    </div>
</div>
""", unsafe_allow_html=True)

    with f_col4:
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-icon-wrapper" style="background:rgba(239,68,68,0.12);color:#EF4444;border:1px solid rgba(239,68,68,0.25);">
        {ICONS['database'].replace('18', '22')}
    </div>
    <div class="feature-title">Forensic Incident Evidence</div>
    <div class="feature-desc">
        Every violation automatically generates high-resolution annotated snapshot evidence, timestamped
        coordinates, worker track ID, and cryptographic database persistence for OSHA audits.
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:54px;'></div>", unsafe_allow_html=True)

    # ── 4. HOW IT WORKS TIMELINE (01 -> 04) ──────────────────────────────────
    st.markdown("""
<div style="text-align:center;margin-bottom:28px;">
    <div style="font-size:0.75rem;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:1px;">
        SEAMLESS DEPLOYMENT PIPELINE
    </div>
    <div style="font-size:1.8rem;font-weight:800;color:var(--text-primary);margin-top:4px;">
        How AEGIS Operates in Production
    </div>
</div>
""", unsafe_allow_html=True)

    t_col1, t_col2, t_col3, t_col4 = st.columns(4)

    with t_col1:
        st.markdown("""
<div class="step-card">
    <div class="step-num">01</div>
    <div class="step-title">Video Ingestion</div>
    <div class="step-desc">
        Connect IP RTSP streams, browser cameras, mobile devices, or recorded site inspections.
    </div>
</div>
""", unsafe_allow_html=True)

    with t_col2:
        st.markdown("""
<div class="step-card">
    <div class="step-num">02</div>
    <div class="step-title">Neural Inference</div>
    <div class="step-desc">
        YOLOv8 runs frame-by-frame inference at 30+ FPS, localizing workers and equipment boundaries.
    </div>
</div>
""", unsafe_allow_html=True)

    with t_col3:
        st.markdown("""
<div class="step-card">
    <div class="step-num">03</div>
    <div class="step-title">Rule Verification</div>
    <div class="step-desc">
        Spatial associator correlates PPE to worker tracks and runs site-specific safety policy rules.
    </div>
</div>
""", unsafe_allow_html=True)

    with t_col4:
        st.markdown("""
<div class="step-card">
    <div class="step-num">04</div>
    <div class="step-title">Instant Dispatch</div>
    <div class="step-desc">
        Violations trigger live dashboard alerts, persist high-res snapshots, and update safety scores.
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:54px;'></div>", unsafe_allow_html=True)

    # ── 5. DASHBOARD PREVIEW / PRODUCT MOCKUP ────────────────────────────────
    st.markdown("""
<div style="text-align:center;margin-bottom:24px;">
    <div style="font-size:0.75rem;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:1px;">
        MISSION CONTROL INTERFACE
    </div>
    <div style="font-size:1.8rem;font-weight:800;color:var(--text-primary);margin-top:4px;">
        Interactive Live Safety Console
    </div>
    <p style="font-size:0.9rem;color:var(--text-secondary);max-width:600px;margin:8px auto 0;">
        The exact interface your safety teams will use to monitor live video feeds, analyze compliance trends, and export forensic logs.
    </p>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="background:var(--bg-card);border:1px solid var(--border-medium);border-radius:16px;padding:16px;box-shadow:var(--shadow-elevated);margin-bottom:48px;">
    <!-- Mockup Header -->
    <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px 14px;border-bottom:1px solid var(--border-subtle);">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#EF4444;"></span>
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#F59E0B;"></span>
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#10B981;"></span>
            <span style="font-size:0.75rem;font-weight:600;color:var(--text-muted);margin-left:10px;">AEGIS Safety Command Center — Site North Zone 3</span>
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
            <span class="badge badge-running">LIVE FEED • 30.2 FPS</span>
        </div>
    </div>
    <!-- Mockup Content -->
    <div style="display:grid;grid-template-columns:2.5fr 1fr;gap:16px;padding-top:16px;">
        <!-- Left: Simulated Viewport -->
        <div style="background:#090D13;border:1px solid var(--border-subtle);border-radius:10px;min-height:280px;display:flex;flex-direction:column;justify-content:space-between;padding:16px;position:relative;overflow:hidden;">
            <div style="display:flex;justify-content:space-between;align-items:center;z-index:2;">
                <span style="font-size:0.72rem;font-family:monospace;color:#10B981;background:rgba(16,185,129,0.12);padding:4px 8px;border-radius:4px;">CAMERA_01 [CRANE SECTOR]</span>
                <span style="font-size:0.72rem;font-family:monospace;color:#F59E0B;">REC ● 00:42:15</span>
            </div>
            <!-- Bounding Box Simulation -->
            <div style="border:2px dashed #EF4444;background:rgba(239,68,68,0.08);width:160px;height:200px;margin:20px auto;border-radius:6px;position:relative;display:flex;flex-direction:column;justify-content:space-between;padding:8px;">
                <span style="font-size:0.68rem;font-weight:700;background:#EF4444;color:#FFF;padding:2px 6px;border-radius:3px;align-self:flex-start;">WKR_104 • NO-Hardhat</span>
                <span style="font-size:0.68rem;color:#EF4444;font-family:monospace;">Conf: 94%</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:var(--text-muted);z-index:2;">
                <span>Sensors: Active</span>
                <span>Active Tracks: 4 Workers</span>
            </div>
        </div>
        <!-- Right: Telemetry Sidebar -->
        <div style="display:flex;flex-direction:column;gap:10px;">
            <div style="background:var(--bg-card-2);border:1px solid var(--border-subtle);border-radius:8px;padding:12px;">
                <div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;">Site Safety Score</div>
                <div style="font-size:1.6rem;font-weight:900;color:#10B981;">98.4%</div>
            </div>
            <div style="background:var(--bg-card-2);border:1px solid var(--border-subtle);border-radius:8px;padding:12px;">
                <div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;">Active Violations</div>
                <div style="font-size:1.6rem;font-weight:900;color:#EF4444;">1 Breached</div>
            </div>
            <div style="background:var(--bg-card-2);border:1px solid var(--border-subtle);border-radius:8px;padding:12px;">
                <div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;">Total Scanned</div>
                <div style="font-size:1.4rem;font-weight:700;color:var(--text-primary);">14,820 Frames</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── 6. FINAL CONVERSION CTA BANNER ───────────────────────────────────────
    st.markdown("""
<div style="text-align:center;padding:48px 24px;background:radial-gradient(circle at 50% 50%, rgba(245,158,11,0.15) 0%, rgba(13,18,27,0.95) 75%);border-radius:20px;border:1px solid rgba(245,158,11,0.25);margin-bottom:36px;">
    <div style="font-size:2rem;font-weight:800;color:var(--text-primary);margin-bottom:10px;">
        Ready to Transform Worksite Safety?
    </div>
    <p style="font-size:1rem;color:var(--text-secondary);max-width:600px;margin:0 auto 28px;">
        Join safety inspectors, project engineers, and compliance officers who trust AEGIS
        for automated, high-precision worksite oversight.
    </p>
</div>
""", unsafe_allow_html=True)

    c_final_l, c_final_m, c_final_r = st.columns([1.5, 2, 1.5])
    with c_final_m:
        if st.button("🚀 Get Started with AEGIS Now", key="final_cta_btn", use_container_width=True):
            st.session_state.active_view = "signup"
            st.rerun()

    # ── 7. FOOTER ────────────────────────────────────────────────────────────
    st.markdown("""
<div style="height:1px;background:var(--border-subtle);margin:40px 0 20px;"></div>
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;padding-bottom:20px;">
    <div style="font-size:0.78rem;color:var(--text-muted);">
        © 2026 AEGIS AI Technologies Inc. All rights reserved. • Enterprise Safety Intelligence
    </div>
    <div style="display:flex;align-items:center;gap:16px;font-size:0.78rem;color:var(--text-secondary);">
        <span>ISO-45001 Compliant</span>
        <span>•</span>
        <span>OSHA Standard 1926 Aligned</span>
        <span>•</span>
        <span style="color:#10B981;">● All Systems Operational</span>
    </div>
</div>
""", unsafe_allow_html=True)
