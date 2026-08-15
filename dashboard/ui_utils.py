"""
AEGIS Safety Intelligence — UI Theme System
Supports dark (default) and light themes via session state toggle.
Uses CSS custom properties (variables) for seamless theme switching.
"""
import streamlit as st

# ── Color tokens (Python-side, for chart colours etc.) ───────────────────────
ORANGE = "#f97316"
AMBER  = "#fbbf24"
RED    = "#ef4444"
GREEN  = "#22c55e"
TEAL   = "#06b6d4"
BLUE   = "#3b82f6"

# ── Theme palette definitions ─────────────────────────────────────────────────
THEMES = {
    "dark": {
        "--bg-base":     "#0f1117",
        "--bg-surface":  "#1c2130",
        "--bg-elevated": "#232b3e",
        "--bg-overlay":  "#2d3650",
        "--border":      "rgba(255,255,255,0.08)",
        "--border-hover":"rgba(249,115,22,0.3)",
        "--text-1":      "#f1f5f9",
        "--text-2":      "rgba(241,245,249,0.6)",
        "--text-muted":  "rgba(241,245,249,0.32)",
        "--shadow":      "0 4px 24px rgba(0,0,0,0.5)",
        "--shadow-sm":   "0 2px 10px rgba(0,0,0,0.35)",
        "--glow-orange": "rgba(249,115,22,0.18)",
        "--sidebar-bg":  "linear-gradient(180deg,#0a0d14 0%,#111827 100%)",
        "--sidebar-border":"rgba(249,115,22,0.1)",
        "--input-bg":    "rgba(255,255,255,0.04)",
        "--input-border":"rgba(255,255,255,0.1)",
    },
    "light": {
        "--bg-base":     "#f0f4f8",
        "--bg-surface":  "#ffffff",
        "--bg-elevated": "#f8fafc",
        "--bg-overlay":  "#e2e8f0",
        "--border":      "rgba(0,0,0,0.09)",
        "--border-hover":"rgba(249,115,22,0.4)",
        "--text-1":      "#0f172a",
        "--text-2":      "rgba(15,23,42,0.6)",
        "--text-muted":  "rgba(15,23,42,0.38)",
        "--shadow":      "0 4px 24px rgba(0,0,0,0.10)",
        "--shadow-sm":   "0 2px 8px rgba(0,0,0,0.07)",
        "--glow-orange": "rgba(249,115,22,0.12)",
        "--sidebar-bg":  "linear-gradient(180deg,#1e293b 0%,#0f172a 100%)",
        "--sidebar-border":"rgba(249,115,22,0.15)",
        "--input-bg":    "rgba(0,0,0,0.03)",
        "--input-border":"rgba(0,0,0,0.12)",
    },
}


def get_theme() -> str:
    """Return current theme ('dark' or 'light') from session state."""
    return st.session_state.get("aegis_theme", "dark")


def render_theme_toggle():
    """Render a compact light/dark toggle in the sidebar."""
    current = get_theme()
    icon    = "☀️" if current == "dark" else "🌙"
    label   = "Switch to Light Mode" if current == "dark" else "Switch to Dark Mode"
    if st.button(f"{icon}  {label}", key="theme_toggle_btn", use_container_width=True):
        st.session_state.aegis_theme = "light" if current == "dark" else "dark"
        st.rerun()


def apply_custom_css():
    """Inject theme-aware CSS via custom properties."""
    theme  = get_theme()
    tokens = THEMES[theme]

    # Build :root variable block
    root_vars = "\n".join(f"        {k}: {v};" for k, v in tokens.items())

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── THEME VARIABLES ──────────────────────────────────────────────────── */
    :root {{
{root_vars}
        --accent:        {ORANGE};
        --accent-dim:    rgba(249,115,22,0.15);
        --red:           {RED};
        --green:         {GREEN};
        --amber:         {AMBER};
        --teal:          {TEAL};
        --blue:          {BLUE};
        --radius:        12px;
        --radius-sm:     8px;
        --transition:    0.2s ease;
    }}

    /* ── GLOBAL ──────────────────────────────────────────────────────────── */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"] {{
        font-family: 'Inter', system-ui, sans-serif !important;
        background: var(--bg-base) !important;
        color: var(--text-1) !important;
    }}

    [data-testid="stAppViewContainer"]::before {{
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 70% 50% at 15% 0%, var(--glow-orange) 0%, transparent 60%),
            radial-gradient(ellipse 45% 40% at 85% 100%, rgba(6,182,212,0.04) 0%, transparent 55%);
        pointer-events: none;
        z-index: 0;
    }}

    code, pre {{ font-family: 'JetBrains Mono', monospace !important; }}

    /* ── SIDEBAR ──────────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border) !important;
    }}
    section[data-testid="stSidebar"] > div {{ padding: 1rem 0.75rem !important; }}

    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {ORANGE} !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        margin: 18px 0 6px !important;
        padding-bottom: 5px !important;
        border-bottom: 1px solid rgba(249,115,22,0.15) !important;
    }}

    /* sidebar text colour always light (sidebar is always dark) */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] div {{
        color: rgba(241,245,249,0.75) !important;
    }}

    /* ── BUTTONS ──────────────────────────────────────────────────────────── */
    .stButton > button {{
        background: linear-gradient(135deg, {ORANGE} 0%, #ea6c0a 100%) !important;
        border: 1px solid rgba(249,115,22,0.4) !important;
        color: #fff !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        padding: 10px 20px !important;
        transition: all var(--transition) !important;
        box-shadow: 0 2px 14px rgba(249,115,22,0.28) !important;
        width: 100% !important;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #fb923c 0%, {ORANGE} 100%) !important;
        box-shadow: 0 4px 22px rgba(249,115,22,0.46) !important;
        transform: translateY(-1px) !important;
    }}
    .stButton > button:active {{ transform: translateY(0) !important; }}

    /* Stop scan variant */
    .stop-btn .stButton > button {{
        background: rgba(239,68,68,0.1) !important;
        border: 1px solid rgba(239,68,68,0.35) !important;
        color: #fca5a5 !important;
        box-shadow: none !important;
    }}
    .stop-btn .stButton > button:hover {{
        background: rgba(239,68,68,0.2) !important;
        box-shadow: 0 4px 16px rgba(239,68,68,0.28) !important;
    }}

    /* Theme toggle button */
    [data-testid="stButton"][aria-label="theme_toggle_btn"] > button,
    button[kind="secondary"] {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: rgba(241,245,249,0.75) !important;
        box-shadow: none !important;
        font-size: 0.75rem !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }}

    /* ── FORM CONTROLS ────────────────────────────────────────────────────── */
    div[data-baseweb="select"] > div {{
        background: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-1) !important;
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
        border: 1.5px dashed rgba(249,115,22,0.3) !important;
        border-radius: var(--radius) !important;
        background: var(--accent-dim) !important;
    }}

    [data-testid="stTextInput"] > div > div > input,
    [data-testid="stNumberInput"] > div > div > input {{
        background: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-1) !important;
    }}
    [data-testid="stTextInput"] > div > div > input:focus {{
        border-color: rgba(249,115,22,0.5) !important;
        box-shadow: 0 0 0 3px rgba(249,115,22,0.1) !important;
    }}

    /* ── KPI CARDS ────────────────────────────────────────────────────────── */
    .kpi-card {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 16px 18px 20px;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
        height: 100%;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow);
        border-color: var(--border-hover);
    }}
    /* Coloured bottom bar */
    .kpi-card::after {{
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0; height: 3px;
        border-radius: 0 0 var(--radius) var(--radius);
    }}
    .kpi-orange::after  {{ background: linear-gradient(90deg,{ORANGE},{AMBER}); }}
    .kpi-red::after     {{ background: linear-gradient(90deg,{RED},#f87171); }}
    .kpi-green::after   {{ background: linear-gradient(90deg,{GREEN},#4ade80); }}
    .kpi-amber::after   {{ background: linear-gradient(90deg,{AMBER},#fde68a); }}
    .kpi-teal::after    {{ background: linear-gradient(90deg,{TEAL},#22d3ee); }}
    .kpi-blue::after    {{ background: linear-gradient(90deg,{BLUE},#60a5fa); }}

    .kpi-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }}
    .kpi-label {{
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--text-muted);
        line-height: 1.3;
        flex: 1;
        padding-right: 8px;
    }}
    .kpi-icon {{
        font-size: 1.2rem;
        opacity: 0.6;
        flex-shrink: 0;
        line-height: 1;
    }}
    .kpi-value {{
        font-size: 1.65rem;
        font-weight: 800;
        color: var(--text-1);
        line-height: 1;
        letter-spacing: -0.5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }}
    .kpi-value-sm {{
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-1);
        line-height: 1.2;
        word-break: break-word;
        overflow-wrap: break-word;
    }}

    /* ── AEGIS CARD (generic container) ──────────────────────────────────── */
    .aegis-card {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: var(--shadow-sm);
        transition: transform var(--transition), border-color var(--transition);
    }}
    .aegis-card:hover {{
        transform: translateY(-2px);
        border-color: var(--border-hover);
    }}

    /* ── VIOLATION CARDS ──────────────────────────────────────────────────── */
    .violation-card {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-left: 3px solid {RED};
        border-radius: var(--radius-sm);
        padding: 11px 14px;
        margin-bottom: 8px;
        box-shadow: var(--shadow-sm);
        transition: border-color var(--transition);
    }}
    .violation-card-critical {{
        border-left-color: {RED};
        background: linear-gradient(135deg, rgba(239,68,68,0.05) 0%, var(--bg-surface) 100%);
    }}
    .violation-card-high {{
        border-left-color: {AMBER};
        background: linear-gradient(135deg, rgba(251,191,36,0.04) 0%, var(--bg-surface) 100%);
    }}
    .violation-card-resolved {{
        border-left-color: {GREEN};
        background: linear-gradient(135deg, rgba(34,197,94,0.04) 0%, var(--bg-surface) 100%);
    }}

    /* ── STATUS BADGES ────────────────────────────────────────────────────── */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 9px;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        white-space: nowrap;
    }}
    .badge-critical {{ background: rgba(239,68,68,0.12);  color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }}
    .badge-high     {{ background: rgba(251,191,36,0.12); color: #fde68a; border: 1px solid rgba(251,191,36,0.3); }}
    .badge-safe     {{ background: rgba(34,197,94,0.10);  color: #86efac; border: 1px solid rgba(34,197,94,0.25); }}
    .badge-running  {{ background: rgba(249,115,22,0.12); color: #fdba74; border: 1px solid rgba(249,115,22,0.3); }}
    .badge-info     {{ background: rgba(6,182,212,0.10);  color: #67e8f9; border: 1px solid rgba(6,182,212,0.25); }}

    /* ── SECTION TITLE ────────────────────────────────────────────────────── */
    .section-title {{
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--text-2);
        letter-spacing: 0.6px;
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

    /* ── BRAND HEADER ─────────────────────────────────────────────────────── */
    .brand-header {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-top: 3px solid {ORANGE};
        border-radius: var(--radius);
        padding: 18px 24px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--shadow);
    }}
    .brand-name {{
        font-size: 1.5rem;
        font-weight: 900;
        color: var(--text-1);
        letter-spacing: 3px;
        line-height: 1;
    }}
    .brand-sub {{
        font-size: 0.6rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 2.5px;
        margin-top: 4px;
    }}

    /* ── SCANNING DOT ─────────────────────────────────────────────────────── */
    .scan-dot {{
        display: inline-block;
        width: 8px; height: 8px;
        background: {ORANGE};
        border-radius: 50%;
        animation: blink 1.2s infinite;
        box-shadow: 0 0 6px {ORANGE};
        margin-right: 5px;
        vertical-align: middle;
    }}
    @keyframes blink {{
        0%,100% {{ opacity:1; }}
        50%      {{ opacity:0.15; }}
    }}

    /* ── DB STATUS ────────────────────────────────────────────────────────── */
    .db-status-ok  {{ color:{GREEN};  font-size:0.68rem; font-weight:600; }}
    .db-status-off {{ color:{AMBER};  font-size:0.68rem; font-weight:600; }}

    /* ── WARNING STRIPE ───────────────────────────────────────────────────── */
    .warning-stripe {{
        background: repeating-linear-gradient(
            -45deg,
            rgba(249,115,22,0.06),
            rgba(249,115,22,0.06) 10px,
            transparent 10px,
            transparent 20px
        );
        border: 1px solid rgba(249,115,22,0.22);
        border-radius: var(--radius-sm);
        padding: 12px 16px;
        font-size: 0.78rem;
        color: #fed7aa;
        margin-bottom: 12px;
    }}

    /* ── SITE STATUS PANELS ───────────────────────────────────────────────── */
    .site-status-safe {{
        background: linear-gradient(135deg, rgba(34,197,94,0.1) 0%, var(--bg-surface) 100%);
        border: 1px solid rgba(34,197,94,0.28);
        border-radius: var(--radius);
        padding: 20px; text-align: center;
    }}
    .site-status-warning {{
        background: linear-gradient(135deg, rgba(251,191,36,0.1) 0%, var(--bg-surface) 100%);
        border: 1px solid rgba(251,191,36,0.28);
        border-radius: var(--radius);
        padding: 20px; text-align: center;
    }}
    .site-status-critical {{
        background: linear-gradient(135deg, rgba(239,68,68,0.12) 0%, var(--bg-surface) 100%);
        border: 1px solid rgba(239,68,68,0.32);
        border-radius: var(--radius);
        padding: 20px; text-align: center;
        animation: pulse-border 2s infinite;
    }}
    @keyframes pulse-border {{
        0%,100% {{ border-color: rgba(239,68,68,0.32); }}
        50%      {{ border-color: rgba(239,68,68,0.65); }}
    }}

    /* ── DATAFRAME ────────────────────────────────────────────────────────── */
    [data-testid="stDataFrame"] {{
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden !important;
    }}

    /* ── HR ───────────────────────────────────────────────────────────────── */
    hr {{ border-color: var(--border) !important; margin: 14px 0 !important; }}

    /* ── SCROLLBAR ────────────────────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(249,115,22,0.25); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(249,115,22,0.45); }}

    /* ── DOWNLOAD BUTTON ──────────────────────────────────────────────────── */
    [data-testid="stDownloadButton"] > button {{
        background: rgba(34,197,94,0.08) !important;
        border: 1px solid rgba(34,197,94,0.25) !important;
        color: #86efac !important;
        font-weight: 600 !important;
        border-radius: var(--radius-sm) !important;
    }}

    /* ── PAGE HEADER ──────────────────────────────────────────────────────── */
    .page-header {{
        margin-bottom: 20px;
        padding-bottom: 14px;
        border-bottom: 1px solid var(--border);
    }}
    .page-header h1 {{
        font-size: 1.6rem;
        font-weight: 900;
        color: var(--text-1);
        letter-spacing: -0.4px;
        margin: 0 0 4px 0;
    }}
    .page-header p {{
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
    }}

    /* ── SESSION ROWS ─────────────────────────────────────────────────────── */
    .session-row {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: border-color var(--transition);
    }}
    .session-row:hover {{ border-color: var(--border-hover); }}

    /* ── EXPANDER ─────────────────────────────────────────────────────────── */
    [data-testid="stExpander"] {{
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden;
    }}

    /* ── MAIN CONTENT WIDTH ───────────────────────────────────────────────── */
    .block-container {{
        padding: 1.5rem 2rem 2rem !important;
        max-width: 1400px !important;
    }}

    </style>
    """, unsafe_allow_html=True)


# ── Component helpers ─────────────────────────────────────────────────────────

def render_brand_header(is_scanning: bool = False, db_ok: bool = True):
    """Render the AEGIS brand header bar."""
    theme   = get_theme()
    dot_html = '<span class="scan-dot"></span>' if is_scanning else ""
    scan_txt = (
        f'{dot_html}<span style="color:{ORANGE};font-size:0.72rem;font-weight:700;">SCANNING</span>'
        if is_scanning else
        '<span style="color:var(--text-muted);font-size:0.72rem;">STANDBY</span>'
    )
    db_html = (
        '<span class="db-status-ok">&#9679; DB CONNECTED</span>'
        if db_ok else
        '<span class="db-status-off">&#9679; DB OFFLINE</span>'
    )
    st.markdown(f"""
    <div class="brand-header">
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="font-size:2.4rem;line-height:1;filter:drop-shadow(0 0 12px rgba(249,115,22,0.45));">&#9937;</div>
            <div>
                <div class="brand-name">AEGIS</div>
                <div class="brand-sub">Construction Safety Intelligence</div>
            </div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
            <div>{scan_txt}</div>
            <div>{db_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, icon: str = "",
             color: str = ORANGE, alert_type: str = None):
    """Render a KPI card. Long values auto-switch to smaller font."""
    color_map = {
        RED:   "kpi-red",
        GREEN: "kpi-green",
        AMBER: "kpi-amber",
        TEAL:  "kpi-teal",
        BLUE:  "kpi-blue",
    }
    css_cls = color_map.get(color, "kpi-orange")
    if alert_type == "danger":   css_cls = "kpi-red"
    if alert_type == "success":  css_cls = "kpi-green"

    # Long values (>6 chars or contains space) get smaller font
    val_cls = "kpi-value-sm" if (len(str(value)) > 6 or " " in str(value)) else "kpi-value"

    st.markdown(f"""
    <div class="kpi-card {css_cls}">
        <div class="kpi-header">
            <div class="kpi-label">{label}</div>
            <div class="kpi-icon">{icon}</div>
        </div>
        <div class="{val_cls}">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def draw_site_status(total_violations: int, critical: int):
    """Render the SITE STATUS panel."""
    if critical > 0:
        css_cls = "site-status-critical"
        icon, title, sub = "🚨", "CRITICAL ALERT", f"{critical} critical violation{'s' if critical!=1 else ''} active"
        color = RED
    elif total_violations > 0:
        css_cls = "site-status-warning"
        icon, title, sub = "⚠️", "ATTENTION REQUIRED", f"{total_violations} violation{'s' if total_violations!=1 else ''} detected"
        color = AMBER
    else:
        css_cls = "site-status-safe"
        icon, title, sub = "✅", "SITE CLEAR", "All workers compliant"
        color = GREEN

    st.markdown(f"""
    <div class="{css_cls}">
        <div style="font-size:2rem;margin-bottom:8px;">{icon}</div>
        <div style="font-size:0.85rem;font-weight:800;color:{color};letter-spacing:1px;">{title}</div>
        <div style="font-size:0.72rem;color:var(--text-muted);margin-top:5px;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def draw_violation_feed_card(timestamp: str, violation_type: str, worker_id: str,
                              confidence: float, severity: str = "HIGH", status: str = "Violation"):
    """Render a single violation in the live feed."""
    if status == "Resolved":
        card_cls, badge_cls, badge_txt, dot = "violation-card violation-card-resolved", "badge badge-safe",     "RESOLVED", "🟢"
    elif severity == "CRITICAL":
        card_cls, badge_cls, badge_txt, dot = "violation-card violation-card-critical", "badge badge-critical",  "CRITICAL", "🔴"
    else:
        card_cls, badge_cls, badge_txt, dot = "violation-card violation-card-high",     "badge badge-high",      severity,   "🟡"

    st.markdown(f"""
    <div class="{card_cls}">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.67rem;color:var(--text-muted);">{timestamp}</span>
            <span class="{badge_cls}">{dot} {badge_txt}</span>
        </div>
        <div style="font-size:0.86rem;font-weight:700;color:var(--text-1);margin-bottom:4px;">{violation_type}</div>
        <div style="display:flex;justify-content:space-between;">
            <span style="font-size:0.7rem;color:var(--text-muted);">Worker: <b style="color:#fdba74;">{worker_id}</b></span>
            <span style="font-size:0.7rem;color:var(--text-muted);">Conf: <b style="color:{TEAL};font-family:'JetBrains Mono',monospace;">{confidence:.2f}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Backward compat alias
def draw_incident_card(timestamp, breach_type, worker_id, confidence, snap_path, status):
    severity = "CRITICAL" if ("Hardhat" in breach_type or "Vest" in breach_type) else "HIGH"
    draw_violation_feed_card(timestamp, breach_type, worker_id, confidence, severity, status)


def mission_control_header(title: str, subtitle: str):
    """Page-level header."""
    st.markdown(f"""
    <div class="page-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def navigation_tip():
    """Sidebar nav tip."""
    st.markdown(f"""
    <div style="padding:12px 14px;border-radius:10px;background:rgba(249,115,22,0.06);
        border:1px solid rgba(249,115,22,0.15);margin:12px 0;">
        <div style="color:{ORANGE};font-weight:700;font-size:0.68rem;text-transform:uppercase;
            letter-spacing:1px;margin-bottom:4px;">&#9937; Navigation</div>
        <div style="color:rgba(241,245,249,0.45);font-size:0.73rem;line-height:1.5;">
            <b style="color:rgba(241,245,249,0.7);">Safety Monitor</b> &#8226;
            <b style="color:rgba(241,245,249,0.7);">Analytics</b> &#8226;
            <b style="color:rgba(241,245,249,0.7);">Incident Explorer</b>
        </div>
    </div>
    """, unsafe_allow_html=True)


def standby_placeholder():
    """Standby screen."""
    st.markdown(f"""
    <div style="background:var(--bg-surface);border:1.5px dashed rgba(249,115,22,0.2);
        border-radius:var(--radius);padding:80px 20px;text-align:center;">
        <div style="font-size:3rem;margin-bottom:14px;filter:drop-shadow(0 0 16px rgba(249,115,22,0.3));">&#128249;</div>
        <div style="font-size:0.95rem;font-weight:800;color:var(--text-1);letter-spacing:0.5px;margin-bottom:8px;">
            SAFETY MONITOR STANDBY</div>
        <div style="width:36px;height:2px;background:linear-gradient(90deg,{ORANGE},{AMBER});
            margin:0 auto 12px;border-radius:2px;"></div>
        <p style="color:var(--text-muted);font-size:0.8rem;max-width:360px;margin:0 auto;line-height:1.6;">
            Select an input source from the sidebar and click
            <b style="color:{ORANGE};">&#9654; START SCAN</b> to begin monitoring.
        </p>
    </div>
    """, unsafe_allow_html=True)


def scan_complete_placeholder(violations: int, frames: int, duration: str = ""):
    """Post-scan completion banner."""
    score = max(0, round((1 - violations / max(frames, 1)) * 100, 1)) if frames > 0 else 100.0
    score_color = GREEN if score >= 80 else AMBER if score >= 50 else RED
    st.markdown(f"""
    <div style="background:var(--bg-surface);border:1px solid rgba(34,197,94,0.2);
        border-top:3px solid {GREEN};border-radius:var(--radius);padding:50px 20px;text-align:center;">
        <div style="font-size:2.8rem;margin-bottom:12px;filter:drop-shadow(0 0 16px rgba(34,197,94,0.3));">&#9937;</div>
        <div style="font-size:0.95rem;font-weight:800;color:var(--text-1);letter-spacing:0.5px;margin-bottom:6px;">
            SCAN SESSION COMPLETE</div>
        <div style="width:36px;height:2px;background:linear-gradient(90deg,{GREEN},{TEAL});
            margin:0 auto 12px;border-radius:2px;"></div>
        <p style="color:var(--text-muted);font-size:0.8rem;max-width:420px;margin:0 auto;line-height:1.7;">
            <b style="color:{GREEN};">{violations} unique violations</b> logged across
            <b style="color:{TEAL};">{frames} frames</b>
            {f'in <b style="color:{AMBER};">{duration}</b>' if duration else ''}.
            Safety score: <b style="color:{score_color};">{score}%</b>
        </p>
    </div>
    """, unsafe_allow_html=True)
