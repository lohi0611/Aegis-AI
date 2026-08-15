"""
AEGIS Safety Intelligence — UI Theme
Construction Safety Command Center visual language.
Palette: Charcoal / Construction Orange / Safety Amber / Alert Red / Safe Green
"""
import streamlit as st


# ── Color tokens ─────────────────────────────────────────────────────────────
BG_BASE      = "#1a1f2e"
BG_SURFACE   = "#232937"
BG_ELEVATED  = "#2a3142"
BG_OVERLAY   = "#303751"

ORANGE       = "#f97316"    # Construction helmet orange
AMBER        = "#fbbf24"    # Safety yellow
RED          = "#ef4444"    # Critical / violation
GREEN        = "#22c55e"    # Safe / compliant
TEAL         = "#06b6d4"    # Info / FPS
BLUE         = "#3b82f6"    # Accent blue (secondary)

TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "rgba(241,245,249,0.6)"
TEXT_MUTED   = "rgba(241,245,249,0.35)"


def apply_custom_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── GLOBAL RESET ─────────────────────────────────────────────────────── */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"] {{
        font-family: 'Inter', system-ui, sans-serif !important;
        background: {BG_BASE} !important;
        color: {TEXT_PRIMARY} !important;
    }}

    /* Subtle construction-grid texture overlay */
    [data-testid="stAppViewContainer"]::before {{
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse 70% 50% at 15% 0%, rgba(249,115,22,0.07) 0%, transparent 60%),
            radial-gradient(ellipse 50% 40% at 85% 100%, rgba(6,182,212,0.04) 0%, transparent 55%);
        pointer-events: none;
        z-index: 0;
    }}

    /* ── TYPOGRAPHY ────────────────────────────────────────────────────────── */
    code, pre {{ font-family: 'JetBrains Mono', monospace !important; }}

    /* ── SIDEBAR ───────────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #151922 0%, #1a1f2e 100%) !important;
        border-right: 1px solid rgba(249,115,22,0.12) !important;
    }}
    section[data-testid="stSidebar"] > div {{ padding: 1rem 0.75rem !important; }}

    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {ORANGE} !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.8px !important;
        text-transform: uppercase !important;
        margin: 20px 0 8px !important;
        padding-bottom: 5px !important;
        border-bottom: 1px solid rgba(249,115,22,0.15) !important;
    }}

    /* ── BUTTONS ───────────────────────────────────────────────────────────── */
    .stButton > button {{
        background: linear-gradient(135deg, {ORANGE} 0%, #ea6c0a 100%) !important;
        border: 1px solid rgba(249,115,22,0.4) !important;
        color: #fff !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        padding: 9px 18px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 12px rgba(249,115,22,0.3) !important;
        width: 100% !important;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #fb923c 0%, {ORANGE} 100%) !important;
        box-shadow: 0 4px 20px rgba(249,115,22,0.5) !important;
        transform: translateY(-1px) !important;
    }}
    .stButton > button:active {{ transform: translateY(0) !important; }}

    /* Stop scan button — secondary */
    .stop-btn .stButton > button {{
        background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.08)) !important;
        border: 1px solid rgba(239,68,68,0.4) !important;
        color: #fca5a5 !important;
        box-shadow: none !important;
    }}
    .stop-btn .stButton > button:hover {{
        background: rgba(239,68,68,0.25) !important;
        box-shadow: 0 4px 16px rgba(239,68,68,0.3) !important;
    }}

    /* ── FORM CONTROLS ─────────────────────────────────────────────────────── */
    div[data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: {TEXT_PRIMARY} !important;
    }}
    div[data-baseweb="select"] > div:focus-within {{
        border-color: rgba(249,115,22,0.5) !important;
        box-shadow: 0 0 0 3px rgba(249,115,22,0.1) !important;
    }}

    .stSlider [role="slider"] {{
        background: {ORANGE} !important;
        box-shadow: 0 0 0 4px rgba(249,115,22,0.2) !important;
    }}

    [data-testid="stFileUploader"] {{
        border: 1px dashed rgba(249,115,22,0.3) !important;
        border-radius: 10px !important;
        background: rgba(249,115,22,0.03) !important;
    }}

    [data-baseweb="tag"] {{
        background: rgba(249,115,22,0.15) !important;
        border: 1px solid rgba(249,115,22,0.35) !important;
        border-radius: 5px !important;
        color: #fed7aa !important;
    }}

    [data-testid="stTextInput"] > div > div > input,
    [data-testid="stNumberInput"] > div > div > input {{
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: {TEXT_PRIMARY} !important;
    }}
    [data-testid="stTextInput"] > div > div > input:focus,
    [data-testid="stNumberInput"] > div > div > input:focus {{
        border-color: rgba(249,115,22,0.5) !important;
        box-shadow: 0 0 0 3px rgba(249,115,22,0.1) !important;
    }}

    /* ── CARDS ─────────────────────────────────────────────────────────────── */
    .aegis-card {{
        background: linear-gradient(145deg, {BG_SURFACE} 0%, {BG_ELEVATED} 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: transform 0.2s ease, border-color 0.2s ease;
        position: relative;
        overflow: hidden;
    }}
    .aegis-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    }}
    .aegis-card:hover {{
        transform: translateY(-2px);
        border-color: rgba(249,115,22,0.15);
    }}

    /* ── KPI CARDS ─────────────────────────────────────────────────────────── */
    .kpi-card {{
        background: linear-gradient(145deg, {BG_SURFACE} 0%, {BG_ELEVATED} 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 8px;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.45);
    }}
    .kpi-card::after {{
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0; height: 3px;
        border-radius: 0 0 14px 14px;
    }}
    .kpi-orange::after  {{ background: linear-gradient(90deg, {ORANGE}, #fb923c); box-shadow: 0 0 10px rgba(249,115,22,0.5); }}
    .kpi-red::after     {{ background: linear-gradient(90deg, {RED}, #f87171);    box-shadow: 0 0 10px rgba(239,68,68,0.5); }}
    .kpi-green::after   {{ background: linear-gradient(90deg, {GREEN}, #4ade80);  box-shadow: 0 0 10px rgba(34,197,94,0.5); }}
    .kpi-amber::after   {{ background: linear-gradient(90deg, {AMBER}, #fcd34d);  box-shadow: 0 0 10px rgba(251,191,36,0.5); }}
    .kpi-teal::after    {{ background: linear-gradient(90deg, {TEAL}, #22d3ee);   box-shadow: 0 0 10px rgba(6,182,212,0.5); }}
    .kpi-blue::after    {{ background: linear-gradient(90deg, {BLUE}, #60a5fa);   box-shadow: 0 0 10px rgba(59,130,246,0.5); }}

    .kpi-label {{
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        color: {TEXT_MUTED};
        margin-bottom: 10px;
    }}
    .kpi-value {{
        font-size: 1.9rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
        letter-spacing: -0.5px;
    }}
    .kpi-icon {{
        position: absolute;
        top: 15px; right: 16px;
        font-size: 1.4rem;
        opacity: 0.65;
    }}
    .kpi-sub {{
        font-size: 0.7rem;
        color: {TEXT_MUTED};
        margin-top: 5px;
    }}

    /* ── VIOLATION FEED CARDS ──────────────────────────────────────────────── */
    .violation-card {{
        background: linear-gradient(135deg, rgba(239,68,68,0.07) 0%, {BG_ELEVATED} 100%);
        border: 1px solid rgba(239,68,68,0.2);
        border-left: 3px solid {RED};
        border-radius: 10px;
        padding: 11px 14px;
        margin-bottom: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }}
    .violation-card-critical {{
        background: linear-gradient(135deg, rgba(239,68,68,0.1) 0%, {BG_ELEVATED} 100%);
        border: 1px solid rgba(239,68,68,0.3);
        border-left: 3px solid {RED};
    }}
    .violation-card-high {{
        border-left-color: {AMBER};
        border-color: rgba(251,191,36,0.25);
        background: linear-gradient(135deg, rgba(251,191,36,0.06) 0%, {BG_ELEVATED} 100%);
    }}
    .violation-card-resolved {{
        border-left-color: {GREEN};
        border-color: rgba(34,197,94,0.2);
        background: linear-gradient(135deg, rgba(34,197,94,0.05) 0%, {BG_ELEVATED} 100%);
    }}

    /* ── STATUS BADGES ─────────────────────────────────────────────────────── */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 9px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    .badge-critical  {{ background: rgba(239,68,68,0.15);  color: #fca5a5; border: 1px solid rgba(239,68,68,0.35); }}
    .badge-high      {{ background: rgba(251,191,36,0.15); color: #fde68a; border: 1px solid rgba(251,191,36,0.35); }}
    .badge-safe      {{ background: rgba(34,197,94,0.12);  color: #86efac; border: 1px solid rgba(34,197,94,0.3); }}
    .badge-running   {{ background: rgba(249,115,22,0.15); color: #fdba74; border: 1px solid rgba(249,115,22,0.35); }}
    .badge-info      {{ background: rgba(6,182,212,0.12);  color: #67e8f9; border: 1px solid rgba(6,182,212,0.3); }}

    /* ── SECTION DIVIDERS ──────────────────────────────────────────────────── */
    .section-title {{
        font-size: 0.8rem;
        font-weight: 700;
        color: rgba(241,245,249,0.8);
        letter-spacing: 0.4px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .section-title::after {{
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(249,115,22,0.2), transparent);
    }}

    hr {{ border-color: rgba(255,255,255,0.06) !important; margin: 14px 0 !important; }}

    /* ── STREAMLIT DEFAULTS ────────────────────────────────────────────────── */
    [data-testid="stDataFrame"] {{
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }}

    div[data-testid="stAlert"] {{
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background: rgba(255,255,255,0.03) !important;
    }}

    [data-testid="stDownloadButton"] > button {{
        background: rgba(34,197,94,0.1) !important;
        border: 1px solid rgba(34,197,94,0.3) !important;
        color: #86efac !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }}

    [data-testid="stToast"] {{
        background: {BG_ELEVATED} !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }}

    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.02); }}
    ::-webkit-scrollbar-thumb {{ background: rgba(249,115,22,0.25); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(249,115,22,0.45); }}

    /* ── SITE STATUS PANEL ─────────────────────────────────────────────────── */
    .site-status-safe {{
        background: linear-gradient(135deg, rgba(34,197,94,0.12) 0%, rgba(34,197,94,0.04) 100%);
        border: 1px solid rgba(34,197,94,0.3);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(34,197,94,0.08);
    }}
    .site-status-warning {{
        background: linear-gradient(135deg, rgba(251,191,36,0.12) 0%, rgba(251,191,36,0.04) 100%);
        border: 1px solid rgba(251,191,36,0.3);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(251,191,36,0.08);
    }}
    .site-status-critical {{
        background: linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(239,68,68,0.05) 100%);
        border: 1px solid rgba(239,68,68,0.35);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(239,68,68,0.1);
        animation: pulse-border 2s infinite;
    }}
    @keyframes pulse-border {{
        0%, 100% {{ border-color: rgba(239,68,68,0.35); }}
        50%       {{ border-color: rgba(239,68,68,0.7); }}
    }}

    /* ── SCANNING INDICATOR ────────────────────────────────────────────────── */
    .scan-dot {{
        display: inline-block;
        width: 8px; height: 8px;
        background: {ORANGE};
        border-radius: 50%;
        animation: blink 1.2s infinite;
        box-shadow: 0 0 6px {ORANGE};
        margin-right: 5px;
    }}
    @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50%       {{ opacity: 0.2; }}
    }}

    /* ── DB STATUS INDICATOR ───────────────────────────────────────────────── */
    .db-status-ok  {{ color: {GREEN};  font-size: 0.7rem; font-weight: 600; }}
    .db-status-off {{ color: {AMBER};  font-size: 0.7rem; font-weight: 600; }}

    /* ── STRIPED WARNING BANNER ─────────────────────────────────────────────── */
    .warning-stripe {{
        background: repeating-linear-gradient(
            -45deg,
            rgba(249,115,22,0.08),
            rgba(249,115,22,0.08) 10px,
            transparent 10px,
            transparent 20px
        );
        border: 1px solid rgba(249,115,22,0.25);
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 0.8rem;
        color: #fed7aa;
    }}

    /* ── SESSION HISTORY ROWS ──────────────────────────────────────────────── */
    .session-row {{
        background: {BG_SURFACE};
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: border-color 0.2s ease;
    }}
    .session-row:hover {{ border-color: rgba(249,115,22,0.25); }}

    </style>
    """, unsafe_allow_html=True)


# ── Component helpers ────────────────────────────────────────────────────────

def render_brand_header(is_scanning: bool = False, db_ok: bool = True):
    """Render the main AEGIS brand header with scanning status."""
    scan_indicator = (
        '<span class="scan-dot"></span> <span style="color:#f97316;font-size:0.75rem;font-weight:700;">SCANNING ACTIVE</span>'
        if is_scanning else
        '<span style="color:rgba(241,245,249,0.35);font-size:0.75rem;">STANDBY</span>'
    )
    db_indicator = (
        '<span class="db-status-ok">⬤ DB CONNECTED</span>'
        if db_ok else
        '<span class="db-status-off">⬤ DB OFFLINE (CSV fallback)</span>'
    )
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {BG_SURFACE} 0%, {BG_ELEVATED} 100%);
        border: 1px solid rgba(249,115,22,0.15);
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4), 0 0 0 1px rgba(249,115,22,0.05);
        position: relative;
        overflow: hidden;
    ">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;
            background:linear-gradient(90deg,{ORANGE},{AMBER},transparent);"></div>
        <div style="display:flex;align-items:center;gap:18px;">
            <div style="font-size:2.8rem;filter:drop-shadow(0 0 14px rgba(249,115,22,0.5));line-height:1;">&#9937;</div>
            <div>
                <div style="font-size:1.6rem;font-weight:900;color:#ffffff;letter-spacing:3px;line-height:1;">AEGIS</div>
                <div style="font-size:0.65rem;color:rgba(241,245,249,0.4);text-transform:uppercase;letter-spacing:2.5px;margin-top:3px;">Construction Safety Intelligence</div>
            </div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
            <div>{scan_indicator}</div>
            <div>{db_indicator}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, icon: str = "🔹",
             color: str = ORANGE, alert_type: str = None):
    """Render a KPI card with construction-safety styling."""
    color_class = "kpi-orange"
    if alert_type == "danger" or color in (RED, "#f85149", "#ef4444"):
        color_class = "kpi-red"
    elif alert_type == "success" or color in (GREEN, "#22c55e", "#10b981", "#56d364"):
        color_class = "kpi-green"
    elif color in (AMBER, "#fbbf24", "#e3b341"):
        color_class = "kpi-amber"
    elif color in (TEAL, "#06b6d4", "#00d4ff", "#38bdf8"):
        color_class = "kpi-teal"
    elif color in (BLUE, "#3b82f6", "#58a6ff"):
        color_class = "kpi-blue"

    st.markdown(f"""
    <div class="kpi-card {color_class}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def draw_site_status(total_violations: int, critical: int):
    """Render the SITE STATUS panel based on live detection state."""
    if critical > 0:
        css_class = "site-status-critical"
        icon = "🔴"
        title = "CRITICAL VIOLATIONS"
        sub = f"{critical} critical event{'s' if critical != 1 else ''} detected"
    elif total_violations > 0:
        css_class = "site-status-warning"
        icon = "🟡"
        title = "ATTENTION REQUIRED"
        sub = f"{total_violations} violation{'s' if total_violations != 1 else ''} in progress"
    else:
        css_class = "site-status-safe"
        icon = "🟢"
        title = "SITE SAFE"
        sub = "No violations detected"

    st.markdown(f"""
    <div class="{css_class}">
        <div style="font-size:2rem;margin-bottom:8px;">{icon}</div>
        <div style="font-size:0.85rem;font-weight:800;color:#ffffff;letter-spacing:1px;">{title}</div>
        <div style="font-size:0.72rem;color:rgba(241,245,249,0.5);margin-top:5px;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def draw_violation_feed_card(timestamp: str, violation_type: str, worker_id: str,
                              confidence: float, severity: str = "HIGH", status: str = "Violation"):
    """Render a single violation in the live feed."""
    if status == "Resolved":
        card_cls = "violation-card violation-card-resolved"
        dot = "🟢"
        badge_cls = "badge badge-safe"
        badge_txt = "RESOLVED"
    elif severity == "CRITICAL":
        card_cls = "violation-card violation-card-critical"
        dot = "🔴"
        badge_cls = "badge badge-critical"
        badge_txt = "CRITICAL"
    else:
        card_cls = "violation-card violation-card-high"
        dot = "🟡"
        badge_cls = "badge badge-high"
        badge_txt = severity

    st.markdown(f"""
    <div class="{card_cls}">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                color:rgba(241,245,249,0.35);">{timestamp}</span>
            <span class="{badge_cls}">{dot} {badge_txt}</span>
        </div>
        <div style="font-size:0.88rem;font-weight:700;color:#ffffff;margin-bottom:4px;">{violation_type}</div>
        <div style="display:flex;justify-content:space-between;">
            <span style="font-size:0.72rem;color:rgba(241,245,249,0.4);">
                Worker: <b style="color:#fdba74;">{worker_id}</b>
            </span>
            <span style="font-size:0.72rem;color:rgba(241,245,249,0.4);">
                Conf: <b style="color:{TEAL};font-family:'JetBrains Mono',monospace;">{confidence:.2f}</b>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Keep backward-compat aliases
def draw_incident_card(timestamp, breach_type, worker_id, confidence, snap_path, status):
    severity = "CRITICAL" if "Hardhat" in breach_type or "Vest" in breach_type else "HIGH"
    draw_violation_feed_card(timestamp, breach_type, worker_id, confidence, severity, status)


def mission_control_header(title: str, subtitle: str):
    """Legacy header — kept for pages that still use it."""
    st.markdown(f"""
    <div style="margin-bottom:16px;">
        <h1 style="font-size:1.8rem;font-weight:900;color:#ffffff;
            letter-spacing:-0.5px;margin-bottom:4px;">{title}</h1>
        <p style="font-size:0.7rem;color:rgba(241,245,249,0.35);
            text-transform:uppercase;letter-spacing:2px;">{subtitle}</p>
        <div style="height:2px;background:linear-gradient(90deg,{ORANGE},transparent);
            margin-top:10px;border-radius:2px;max-width:200px;"></div>
    </div>
    """, unsafe_allow_html=True)


def navigation_tip():
    st.markdown(f"""
    <div style="
        padding: 12px 14px;
        border-radius: 10px;
        background: rgba(249,115,22,0.06);
        border: 1px solid rgba(249,115,22,0.15);
        margin: 16px 0;
    ">
        <div style="color:{ORANGE};font-weight:700;font-size:0.7rem;
            text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">⛑️ Navigation</div>
        <div style="color:rgba(241,245,249,0.45);font-size:0.75rem;line-height:1.5;">
            Use the sidebar to switch between
            <b style="color:rgba(241,245,249,0.7);">Safety Monitor</b>,
            <b style="color:rgba(241,245,249,0.7);">Analytics</b> &amp;
            <b style="color:rgba(241,245,249,0.7);">Incident Explorer</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)


def standby_placeholder():
    """Render the standby video area."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(249,115,22,0.04) 0%, {BG_ELEVATED} 100%);
        border: 1px dashed rgba(249,115,22,0.2);
        border-radius: 14px;
        padding: 80px 20px;
        text-align: center;
    ">
        <div style="font-size:3.5rem;margin-bottom:16px;
            filter:drop-shadow(0 0 18px rgba(249,115,22,0.35));">📹</div>
        <div style="font-size:1rem;font-weight:800;color:#ffffff;
            letter-spacing:0.5px;margin-bottom:8px;">SAFETY MONITOR STANDBY</div>
        <div style="width:36px;height:2px;background:linear-gradient(90deg,{ORANGE},{AMBER});
            margin:0 auto 12px;"></div>
        <p style="color:rgba(241,245,249,0.35);font-size:0.8rem;
            max-width:360px;margin:0 auto;line-height:1.6;">
            Select an input source from the sidebar and click
            <b style="color:{ORANGE};">▶ START SCAN</b> to begin monitoring.
        </p>
    </div>
    """, unsafe_allow_html=True)


def scan_complete_placeholder(violations: int, frames: int, duration: str = ""):
    """Render the post-scan completion banner."""
    score = max(0, round((1 - violations / max(frames, 1)) * 100, 1)) if frames > 0 else 100.0
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(34,197,94,0.08) 0%, {BG_ELEVATED} 100%);
        border: 1px solid rgba(34,197,94,0.2);
        border-radius: 14px;
        padding: 50px 20px;
        text-align: center;
    ">
        <div style="font-size:3rem;margin-bottom:14px;
            filter:drop-shadow(0 0 18px rgba(34,197,94,0.35));">⛑️</div>
        <div style="font-size:1rem;font-weight:800;color:#ffffff;
            letter-spacing:0.5px;margin-bottom:6px;">SCAN SESSION COMPLETE</div>
        <div style="width:36px;height:2px;background:linear-gradient(90deg,{GREEN},{TEAL});
            margin:0 auto 12px;"></div>
        <p style="color:rgba(241,245,249,0.5);font-size:0.8rem;
            max-width:420px;margin:0 auto;line-height:1.7;">
            <b style="color:{GREEN};">{violations} unique violations</b> logged across
            <b style="color:{TEAL};">{frames} frames</b>
            {f'in <b style="color:{AMBER};">{duration}</b>' if duration else ''}.
            Safety score: <b style="color:{ORANGE};">{score}%</b>
        </p>
    </div>
    """, unsafe_allow_html=True)
