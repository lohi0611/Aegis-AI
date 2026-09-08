"""
AEGIS Safety Intelligence — Premium UI System
Construction Safety Command Center
Dark-first design with light theme support via CSS custom properties.
"""
import streamlit as st

# ── Python colour tokens (for Plotly / Python-side logic only) ────────────────
ORANGE = "#F59E0B"   # Industrial safety amber — authoritative primary accent
RED    = "#EF4444"   # Safety hazard red (clean modern coral)
GREEN  = "#10B981"   # Compliance green (emerald)
TEAL   = "#06B6D4"   # Cyan/teal — technical telemetry
BLUE   = "#3B82F6"   # Technical blue — info
AMBER  = "#F59E0B"   # Amber

# ── SVG icon library (clean Lucide-style vectors) ──────────────────────────────
ICONS = {
    "shield": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>""",
    "hardhat": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 18h20"/><path d="M12 3C8 3 4 7 4 12h16c0-5-4-9-8-9z"/><path d="M4 12v3a1 1 0 001 1h14a1 1 0 001-1v-3"/></svg>""",
    "alert-triangle": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>""",
    "check-circle": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>""",
    "camera": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>""",
    "database": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>""",
    "activity": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>""",
    "eye": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>""",
    "clock": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>""",
    "zap": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "x-circle": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>""",
    "sun": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>""",
    "moon": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>""",
    "cpu": """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>""",
}

# ── Theme definitions ─────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "--bg-base":          "#080C12",
        "--bg-sidebar":       "#0D121B",
        "--bg-card":          "rgba(16, 22, 33, 0.82)",
        "--bg-card-2":        "rgba(20, 28, 42, 0.88)",
        "--bg-card-3":        "#182232",
        "--bg-input":         "rgba(255,255,255,0.04)",
        "--border-subtle":    "rgba(255,255,255,0.07)",
        "--border-medium":    "rgba(255,255,255,0.12)",
        "--border-accent":    "rgba(245,158,11,0.30)",
        "--text-primary":     "#F1F5F9",
        "--text-secondary":   "rgba(241,245,249,0.65)",
        "--text-muted":       "rgba(241,245,249,0.35)",
        "--shadow-card":      "0 2px 8px rgba(0,0,0,0.35), 0 12px 32px rgba(0,0,0,0.25)",
        "--shadow-elevated":  "0 8px 36px rgba(0,0,0,0.60)",
        "--accent-primary":   "#F59E0B",
        "--accent-glow":      "rgba(245,158,11,0.14)",
        "--plotly-template":  "plotly_dark",
        "--plotly-paper":     "rgba(0,0,0,0)",
        "--plotly-bg":        "rgba(0,0,0,0)",
        "--plotly-grid":      "rgba(255,255,255,0.04)",
        "--plotly-text":      "rgba(241,245,249,0.45)",
    },
    "light": {
        "--bg-base":          "#F1F5F9",
        "--bg-sidebar":       "#0F172A",
        "--bg-card":          "#FFFFFF",
        "--bg-card-2":        "#F8FAFC",
        "--bg-card-3":        "#F1F5F9",
        "--bg-input":         "rgba(0,0,0,0.03)",
        "--border-subtle":    "rgba(0,0,0,0.08)",
        "--border-medium":    "rgba(0,0,0,0.14)",
        "--border-accent":    "rgba(245,158,11,0.40)",
        "--text-primary":     "#0F172A",
        "--text-secondary":   "rgba(15,23,42,0.65)",
        "--text-muted":       "rgba(15,23,42,0.40)",
        "--shadow-card":      "0 2px 6px rgba(0,0,0,0.06), 0 12px 28px rgba(0,0,0,0.04)",
        "--shadow-elevated":  "0 8px 30px rgba(0,0,0,0.12)",
        "--accent-primary":   "#D97706",
        "--accent-glow":      "rgba(217,119,6,0.10)",
        "--plotly-template":  "plotly_white",
        "--plotly-paper":     "rgba(0,0,0,0)",
        "--plotly-bg":        "rgba(0,0,0,0)",
        "--plotly-grid":      "rgba(0,0,0,0.06)",
        "--plotly-text":      "rgba(15,23,42,0.50)",
    },
}


def get_theme() -> str:
    return st.session_state.get("aegis_theme", "dark")


def apply_custom_css():
    theme  = get_theme()
    tokens = THEMES[theme]
    root_vars = "\n".join(f"    {k}: {v};" for k, v in tokens.items())

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── VARIABLES ─────────────────────────────────────────────── */
:root {{
{root_vars}
    --accent:       {ORANGE};
    --red:          {RED};
    --green:        {GREEN};
    --teal:         {TEAL};
    --amber:        {AMBER};
    --r:            10px;
    --r-sm:         6px;
    --r-lg:         14px;
    --t:            0.18s cubic-bezier(0.16, 1, 0.3, 1);
}}

/* ── GLOBAL STYLES & FONT STABILITY ────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background: var(--bg-base) !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased;
    font-feature-settings: "cv02", "cv03", "cv04", "cv11";
}}

/* Crisp numbers that never jitter when updating */
.kpi-value, .kpi-value-sm, .tabular, [data-testid="stMetricValue"] {{
    font-variant-numeric: tabular-nums !important;
}}

code, pre {{ font-family: 'JetBrains Mono', 'Fira Code', monospace !important; }}

/* ── KILL AMATEUR STREAMLIT CHROME ──────────────────────────── */
#MainMenu, footer, [data-testid="stDeployButton"],
header[data-testid="stHeader"] {{
    display: none !important;
    height: 0 !important;
}}
/* Kill ugly heading anchor hover links */
a.header-anchor, a.anchorjs-link {{
    display: none !important;
}}
.block-container {{
    padding: 1.25rem 2rem 2.5rem !important;
    max-width: 1480px !important;
}}

/* ── SLEEK INDUSTRIAL SCROLLBAR ────────────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
    background: rgba(255,255,255,0.12);
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: var(--accent-primary);
}}

/* ── SIDEBAR ELEVATION ──────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-subtle) !important;
    min-width: 270px !important;
    max-width: 290px !important;
}}
section[data-testid="stSidebar"] > div {{ padding: 0 !important; }}
section[data-testid="stSidebar"] label {{
    color: rgba(241,245,249,0.7) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}}
section[data-testid="stSidebar"] p {{ color: rgba(241,245,249,0.55) !important; }}

/* ── BUTTONS ─────────────────────────────────────────────────── */
.stButton > button {{
    background: linear-gradient(180deg, #F59E0B 0%, #D97706 100%) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #090D13 !important;
    border-radius: var(--r-sm) !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.4px !important;
    padding: 10px 18px !important;
    transition: all var(--t) !important;
    box-shadow: 0 2px 10px rgba(245,158,11,0.25) !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    background: linear-gradient(180deg, #FBBF24 0%, #F59E0B 100%) !important;
    box-shadow: 0 4px 18px rgba(245,158,11,0.40) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* Stop scan button */
.stop-btn .stButton > button {{
    background: rgba(239,68,68,0.12) !important;
    border: 1px solid rgba(239,68,68,0.35) !important;
    color: #F87171 !important;
    box-shadow: none !important;
    font-weight: 600 !important;
}}
.stop-btn .stButton > button:hover {{
    background: rgba(239,68,68,0.22) !important;
    box-shadow: 0 4px 16px rgba(239,68,68,0.30) !important;
    color: #FECACA !important;
}}

/* Icon-only theme toggle */
.theme-btn .stButton > button {{
    background: transparent !important;
    border: 1px solid var(--border-medium) !important;
    color: var(--text-secondary) !important;
    box-shadow: none !important;
    padding: 6px 10px !important;
    font-size: 0.82rem !important;
    width: auto !important;
    min-width: 36px !important;
    border-radius: 50% !important;
    font-weight: 400 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}}
.theme-btn .stButton > button:hover {{
    background: var(--accent-glow) !important;
    border-color: var(--border-accent) !important;
    color: var(--accent-primary) !important;
    transform: none !important;
    box-shadow: none !important;
}}

/* Download button */
[data-testid="stDownloadButton"] > button {{
    background: rgba(46,125,50,0.08) !important;
    border: 1px solid rgba(46,125,50,0.25) !important;
    color: #81C784 !important;
    font-weight: 600 !important;
    border-radius: var(--r-sm) !important;
    box-shadow: none !important;
}}

/* ── FORM INPUTS ─────────────────────────────────────────────── */
div[data-baseweb="select"] > div {{
    background: var(--bg-input) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-primary) !important;
    font-size: 0.85rem !important;
}}
div[data-baseweb="select"] > div:focus-within {{
    border-color: rgba(249,168,37,0.5) !important;
    box-shadow: 0 0 0 3px rgba(249,168,37,0.08) !important;
}}
/* Dropdown menu */
[data-baseweb="popover"] [data-baseweb="menu"] {{
    background: {"#1B2430" if theme == "dark" else "#ffffff"} !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--r-sm) !important;
}}

.stSlider [role="slider"] {{
    background: #F9A825 !important;
    box-shadow: 0 0 0 4px rgba(249,168,37,0.18) !important;
}}
.stSlider [data-testid="stSliderTrackFill"] {{
    background: #F9A825 !important;
}}

[data-testid="stFileUploader"] {{
    border: 1.5px dashed rgba(249,168,37,0.25) !important;
    border-radius: var(--r) !important;
    background: rgba(249,168,37,0.03) !important;
}}

[data-baseweb="tag"] {{
    background: rgba(249,168,37,0.12) !important;
    border: 1px solid rgba(249,168,37,0.3) !important;
    border-radius: 5px !important;
    color: #FFD54F !important;
}}

/* Checkbox */
[data-testid="stCheckbox"] span {{
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
}}

/* ── KPI CARDS ───────────────────────────────────────────────── */
/* ── KPI CARDS (STABILIZED HEIGHT) ─────────────────────────── */
.kpi-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r);
    padding: 14px 16px 16px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-card);
    transition: transform var(--t), box-shadow var(--t), border-color var(--t);
    min-height: 104px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow-elevated);
    border-color: var(--border-medium);
}}
/* Left accent strip */
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 12px; bottom: 12px; left: 0;
    width: 3.5px;
    border-radius: 0 2px 2px 0;
}}
.kpi-yellow::before  {{ background: #F59E0B; }}
.kpi-red::before     {{ background: #EF4444; }}
.kpi-green::before   {{ background: #10B981; }}
.kpi-teal::before    {{ background: #06B6D4; }}
.kpi-blue::before    {{ background: #3B82F6; }}
.kpi-orange::before  {{ background: #F59E0B; }}

.kpi-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    gap: 8px;
}}
.kpi-label {{
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    line-height: 1.2;
}}
.kpi-icon {{
    color: var(--text-muted);
    flex-shrink: 0;
    display: flex;
    align-items: center;
}}
.kpi-value {{
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    letter-spacing: -0.5px;
    font-variant-numeric: tabular-nums;
}}
.kpi-value-sm {{
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
    font-variant-numeric: tabular-nums;
    word-break: break-word;
}}
.kpi-sub {{
    font-size: 0.65rem;
    color: var(--text-muted);
    margin-top: 4px;
}}

/* ── CCTV HUD VIEWPORT ──────────────────────────────────────── */
.cctv-hud {{
    position: relative;
    background: #06090E;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: var(--r);
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    margin-bottom: 12px;
}}
.cctv-hud-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 14px;
    background: rgba(12, 17, 26, 0.95);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.70rem;
    color: rgba(241,245,249,0.7);
    letter-spacing: 0.5px;
}}
.cctv-live-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-weight: 700;
    color: #F59E0B;
}}
.cctv-meta {{
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 0.68rem;
    color: rgba(241,245,249,0.45);
}}

/* ── ZERO-JITTER FIXED-HEIGHT INCIDENT FEED ─────────────────── */
.feed-scroll-box {{
    max-height: 370px;
    min-height: 370px;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 2px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
.v-card {{
    background: var(--bg-card-2);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid #EF4444;
    border-radius: var(--r-sm);
    padding: 10px 12px;
    transition: transform 0.15s ease, border-color 0.15s ease;
    animation: slideIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}}
.v-card:hover {{
    transform: translateX(2px);
    border-color: rgba(255,255,255,0.18);
}}
@keyframes slideIn {{
    from {{ opacity: 0; transform: translateY(-8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.v-card-critical {{ border-left-color: #EF4444; }}
.v-card-high     {{ border-left-color: #F59E0B; }}
.v-card-resolved {{ border-left-color: #10B981; }}

.v-time {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-muted);
}}
.v-type {{
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 3px 0 2px;
}}
.v-meta {{
    font-size: 0.70rem;
    color: var(--text-secondary);
}}

/* ── STATUS BADGES ──────────────────────────────────────────── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2.5px 8px;
    border-radius: 4px;
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    white-space: nowrap;
}}
.badge-critical {{ background: rgba(239,68,68,0.14);  color: #FCA5A5; border: 1px solid rgba(239,68,68,0.35); }}
.badge-high     {{ background: rgba(245,158,11,0.14); color: #FCD34D; border: 1px solid rgba(245,158,11,0.35); }}
.badge-safe     {{ background: rgba(16,185,129,0.14); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.35); }}
.badge-info     {{ background: rgba(6,182,212,0.12);  color: #67E8F9; border: 1px solid rgba(6,182,212,0.30); }}
.badge-running  {{ background: rgba(245,158,11,0.15); color: #FDE68A; border: 1px solid rgba(245,158,11,0.40); }}

/* ── STATUS DOTS ────────────────────────────────────────────── */
.dot {{ display: inline-block; width: 7px; height: 7px; border-radius: 50%; }}
.dot-green   {{ background: #10B981; box-shadow: 0 0 6px rgba(16,185,129,0.5); }}
.dot-amber   {{ background: #F59E0B; box-shadow: 0 0 6px rgba(245,158,11,0.5); }}
.dot-red     {{ background: #EF4444; box-shadow: 0 0 6px rgba(239,68,68,0.5); }}
.dot-grey    {{ background: rgba(241,245,249,0.25); }}
.dot-live    {{ background: #F59E0B; animation: pulse-dot 1.5s infinite; box-shadow: 0 0 8px rgba(245,158,11,0.7); }}
@keyframes pulse-dot {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%       {{ opacity: 0.4; transform: scale(0.85); }}
}}
/* ── BRAND HEADER ───────────────────────────────────────────── */
.brand-header {{
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-top: 2px solid var(--accent-primary);
    border-radius: var(--r);
    padding: 12px 20px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(16px);
}}
.brand-title {{
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: 2px;
    line-height: 1;
}}
.brand-sub {{
    font-size: 0.68rem;
    color: var(--text-muted);
    letter-spacing: 0.5px;
    margin-top: 3px;
}}
.brand-right {{
    display: flex;
    align-items: center;
    gap: 16px;
}}

/* ── SITE STATUS PANELS ─────────────────────────────────────── */
.status-panel {{
    border-radius: var(--r);
    padding: 14px 16px;
    text-align: center;
    border: 1px solid var(--border-subtle);
    background: var(--bg-card);
    box-shadow: var(--shadow-card);
    transition: all var(--t);
}}
.status-safe     {{ border-color: rgba(16,185,129,0.30); background: rgba(16,185,129,0.06); }}
.status-warning  {{ border-color: rgba(245,158,11,0.30); background: rgba(245,158,11,0.06); }}
.status-critical {{
    border-color: rgba(239,68,68,0.40);
    background: rgba(239,68,68,0.08);
    animation: pulse-border 2s infinite;
}}
@keyframes pulse-border {{
    0%, 100% {{ border-color: rgba(239,68,68,0.35); }}
    50%       {{ border-color: rgba(239,68,68,0.70); box-shadow: 0 0 16px rgba(239,68,68,0.25); }}
}}

/* ── HIGH-TECH VIDEO STANDBY VIEWPORT ───────────────────────── */
.video-standby {{
    background: radial-gradient(circle at 50% 50%, rgba(245,158,11,0.05) 0%, #06090E 75%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: var(--r);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 360px;
    padding: 40px 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}}
.video-standby::before {{
    content: '';
    position: absolute;
    width: 240px;
    height: 240px;
    border-radius: 50%;
    border: 1px dashed rgba(245,158,11,0.15);
    animation: radar-sweep 10s linear infinite;
    pointer-events: none;
}}
@keyframes radar-sweep {{
    from {{ transform: rotate(0deg); }}
    to   {{ transform: rotate(360deg); }}
}}
.video-standby-icon {{
    width: 52px; height: 52px;
    border-radius: 12px;
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.30);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 14px;
    color: #F59E0B;
    box-shadow: 0 0 20px rgba(245,158,11,0.20);
}}
.video-standby-title {{
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
    letter-spacing: 0.2px;
}}
.video-standby-sub {{
    font-size: 0.76rem;
    color: var(--text-muted);
    max-width: 320px;
    line-height: 1.5;
    margin: 0 auto 18px;
}}
.ready-indicator {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-size: 0.72rem;
    color: var(--text-secondary);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 4px 10px;
    border-radius: 20px;
}}

/* ── SCAN COMPLETE BANNER ───────────────────────────────────── */
.scan-complete {{
    background: var(--bg-card-2);
    border: 1px solid rgba(46,125,50,0.2);
    border-top: 2px solid #2E7D32;
    border-radius: var(--r);
    padding: 40px 24px;
    text-align: center;
    min-height: 280px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}}

/* ── NAVIGATION TIP ─────────────────────────────────────────── */
.nav-tip {{
    padding: 10px 12px;
    border-radius: var(--r-sm);
    background: rgba(249,168,37,0.05);
    border: 1px solid rgba(249,168,37,0.12);
    margin: 12px 0 6px;
}}

/* ── DATAFRAME ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
}}

/* ── EXPANDERS ──────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important;
}}

/* ── ALERTS / INFO ──────────────────────────────────────────── */
.stAlert {{
    background: var(--bg-card-2) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
}}

/* ── WARNING STRIPE ─────────────────────────────────────────── */
.warning-stripe {{
    background: repeating-linear-gradient(-45deg,rgba(249,168,37,0.05),rgba(249,168,37,0.05) 10px,transparent 10px,transparent 20px);
    border: 1px solid rgba(249,168,37,0.2);
    border-radius: var(--r-sm);
    padding: 10px 14px;
    font-size: 0.78rem;
    color: #FFE082;
    margin-bottom: 10px;
}}

/* ── HR ─────────────────────────────────────────────────────── */
hr {{ border-color: var(--border-subtle) !important; margin: 12px 0 !important; }}


/* ── METRIC WIDGET OVERRIDE ─────────────────────────────────── */
[data-testid="stMetric"] {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--r) !important;
    padding: 14px 18px !important;
    box-shadow: var(--shadow-card) !important;
}}
[data-testid="stMetricLabel"] {{ color: var(--text-secondary) !important; font-size: 0.78rem !important; font-weight: 500 !important; }}
[data-testid="stMetricValue"] {{ color: var(--text-primary) !important; font-size: 1.65rem !important; font-weight: 700 !important; }}

/* ── LANDING PAGE HERO & SECTIONS ────────────────────────── */
.landing-hero {
    position: relative;
    padding: 48px 24px 36px;
    text-align: center;
    background: radial-gradient(circle at 50% 10%, rgba(245, 158, 11, 0.12) 0%, transparent 65%);
    border-radius: 20px;
    border: 1px solid var(--border-subtle);
    margin-bottom: 32px;
    overflow: hidden;
}
.landing-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 9999px;
    background: rgba(245, 158, 11, 0.10);
    border: 1px solid rgba(245, 158, 11, 0.28);
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.landing-title {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1.18;
    color: var(--text-primary);
    margin-bottom: 18px;
    letter-spacing: -0.8px;
}
.landing-title span {
    background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 50%, #10B981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.landing-subtitle {
    font-size: 1.1rem;
    color: var(--text-secondary);
    max-width: 720px;
    margin: 0 auto 30px;
    line-height: 1.6;
}
.landing-stats-row {
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 32px;
    flex-wrap: wrap;
}
.landing-stat-box {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r);
    padding: 16px 24px;
    text-align: center;
    min-width: 150px;
    box-shadow: var(--shadow-card);
    transition: transform var(--t), border-color var(--t);
}
.landing-stat-box:hover {
    transform: translateY(-2px);
    border-color: var(--border-accent);
}
.landing-stat-num {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--accent);
    font-variant-numeric: tabular-nums;
}
.landing-stat-label {
    font-size: 0.74rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}

/* ── FEATURE CARDS ─────────────────────────────────────────── */
.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r-lg);
    padding: 24px;
    height: 100%;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-card);
    transition: all var(--t);
    position: relative;
    overflow: hidden;
}
.feature-card:hover {
    transform: translateY(-3px);
    border-color: var(--border-accent);
    box-shadow: 0 12px 32px rgba(0,0,0,0.35), 0 0 16px var(--accent-glow);
}
.feature-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    flex-shrink: 0;
}
.feature-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.55;
    flex-grow: 1;
}

/* ── TIMELINE 01-04 ─────────────────────────────────────────── */
.step-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r);
    padding: 20px;
    position: relative;
    box-shadow: var(--shadow-card);
    transition: all var(--t);
    height: 100%;
}
.step-card:hover {
    border-color: var(--border-accent);
    transform: translateY(-2px);
}
.step-num {
    font-size: 1.8rem;
    font-weight: 900;
    color: rgba(245, 158, 11, 0.25);
    line-height: 1;
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
}
.step-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 6px;
}
.step-desc {
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* ── AUTH SPLIT SCREEN ──────────────────────────────────────── */
.auth-split-container {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: var(--shadow-elevated);
    margin: 20px auto;
    max-width: 960px;
}
.auth-left-hero {
    background: linear-gradient(135deg, rgba(245,158,11,0.08) 0%, rgba(13,18,27,0.95) 100%);
    border-right: 1px solid var(--border-subtle);
    padding: 40px 32px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.auth-right-form {
    padding: 36px 32px;
}
.auth-strength-bar {
    height: 5px;
    border-radius: 3px;
    background: rgba(255,255,255,0.08);
    overflow: hidden;
    margin-top: 6px;
    margin-bottom: 12px;
}
.auth-strength-fill {
    height: 100%;
    transition: width 0.3s ease, background-color 0.3s ease;
}

/* ── AUTHENTICATED TOP NAV BAR ──────────────────────────────── */
.auth-nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 20px;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r);
    margin-bottom: 18px;
    box-shadow: var(--shadow-card);
}
.user-badge-chip {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--bg-card-2);
    border: 1px solid var(--border-subtle);
    padding: 5px 12px;
    border-radius: 9999px;
}
.user-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #F59E0B, #10B981);
    color: #080C12;
    font-weight: 800;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* ── ACCESS GATE ────────────────────────────────────────────── */
.access-gate-card {
    max-width: 480px;
    margin: 60px auto;
    text-align: center;
    padding: 40px 32px;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r-lg);
    box-shadow: var(--shadow-elevated);
}

</style>
""", unsafe_allow_html=True)


# ── Component functions ────────────────────────────────────────────────────────

def get_plotly_layout_defaults():
    """Return theme-aware Plotly layout kwargs."""
    theme = get_theme()
    t = THEMES[theme]
    is_dark = theme == "dark"
    return {
        "template":     "plotly_dark" if is_dark else "plotly_white",
        "paper_bgcolor": t["--plotly-paper"],
        "plot_bgcolor":  t["--plotly-bg"],
        "font":          dict(family="Inter, sans-serif", color=t["--text-secondary"]),
        "xaxis":         dict(gridcolor=t["--plotly-grid"], tickfont=dict(size=10, color=t["--plotly-text"])),
        "yaxis":         dict(gridcolor=t["--plotly-grid"], tickfont=dict(size=10, color=t["--plotly-text"])),
    }


def render_theme_toggle(key: str = "theme_toggle_main"):
    """Render a compact sun/moon icon button. Returns True if clicked.

    Each call site must pass a unique ``key`` to avoid StreamlitDuplicateElementKey.
    """
    theme   = get_theme()
    # Unicode sun/moon — minimal, clean
    icon    = "&#9788;" if theme == "dark" else "&#9790;"
    tooltip = "Switch to light mode" if theme == "dark" else "Switch to dark mode"
    st.markdown(f'<div class="theme-btn" title="{tooltip}">', unsafe_allow_html=True)
    clicked = st.button(icon, key=key)
    st.markdown("</div>", unsafe_allow_html=True)
    if clicked:
        st.session_state.aegis_theme = "light" if theme == "dark" else "dark"
        st.rerun()


def render_brand_header(is_scanning: bool = False, db_ok: bool = True):
    """Main AEGIS header bar with status info and theme toggle inline."""
    theme = get_theme()
    # Scanning status
    if is_scanning:
        scan_html = '<span class="dot dot-live" style="margin-right:5px;"></span><span style="color:#F9A825;font-size:0.72rem;font-weight:600;">Live</span>'
        badge_html = '<span class="badge badge-running">SCANNING</span>'
    else:
        scan_html = '<span class="dot dot-grey" style="margin-right:5px;"></span><span style="color:var(--text-muted);font-size:0.72rem;">Standby</span>'
        badge_html = '<span class="badge badge-info">READY</span>'

    # DB status
    if db_ok:
        db_html = f'<span class="dot dot-green" style="margin-right:5px;"></span><span style="font-size:0.7rem;color:var(--text-secondary);">Database connected</span>'
    else:
        db_html = f'<span class="dot dot-amber" style="margin-right:5px;"></span><span style="font-size:0.7rem;color:var(--text-secondary);">Database unavailable</span>'

    st.markdown(f"""
<div class="brand-header">
    <div style="display:flex;align-items:center;gap:14px;">
        <div style="width:36px;height:36px;background:rgba(249,168,37,0.12);border:1.5px solid rgba(249,168,37,0.25);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#F9A825;flex-shrink:0;">
            {ICONS['hardhat']}
        </div>
        <div>
            <div class="brand-title">AEGIS AI</div>
            <div class="brand-sub">Construction Safety Intelligence</div>
        </div>
    </div>
    <div class="brand-right">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="display:flex;align-items:center;">{db_html}</div>
            <div style="display:flex;align-items:center;">{scan_html}</div>
            {badge_html}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


def kpi_card(label: str, value: str, icon_key: str = "activity", color_cls: str = "kpi-yellow"):
    """Render a KPI card with left accent strip."""
    icon_svg = ICONS.get(icon_key, "")
    val_cls  = "kpi-value-sm" if (len(str(value)) > 6 or " " in str(value)) else "kpi-value"
    st.markdown(f"""
<div class="kpi-card {color_cls}">
    <div class="kpi-header">
        <div class="kpi-label">{label}</div>
        <div class="kpi-icon">{icon_svg}</div>
    </div>
    <div class="{val_cls}">{value}</div>
</div>
""", unsafe_allow_html=True)


def draw_site_status(total_violations: int, critical: int):
    """Render the site safety condition panel."""
    if critical > 0:
        css_cls = "status-panel status-critical"
        icon_c  = '#D32F2F'
        icon    = ICONS["x-circle"].replace("currentColor", icon_c)
        title   = "Critical condition"
        sub     = f"Immediate review required — {critical} critical event{'s' if critical!=1 else ''}"
        badge   = '<span class="badge badge-critical">CRITICAL</span>'
    elif total_violations > 0:
        css_cls = "status-panel status-warning"
        icon_c  = '#F9A825'
        icon    = ICONS["alert-triangle"].replace("currentColor", icon_c)
        title   = "Attention required"
        sub     = f"{total_violations} active violation{'s' if total_violations!=1 else ''} detected"
        badge   = '<span class="badge badge-high">WARNING</span>'
    else:
        css_cls = "status-panel status-safe"
        icon_c  = '#4CAF50'
        icon    = ICONS["check-circle"].replace("currentColor", icon_c)
        title   = "Site looks safe"
        sub     = "All monitored workers compliant"
        badge   = '<span class="badge badge-safe">CLEAR</span>'

    st.markdown(f"""
<div class="{css_cls}">
    <div style="margin-bottom:8px;">{icon}</div>
    <div style="font-size:0.88rem;font-weight:700;color:var(--text-primary);margin-bottom:4px;">{title}</div>
    <div style="font-size:0.72rem;color:var(--text-secondary);margin-bottom:10px;line-height:1.4;">{sub}</div>
    {badge}
</div>
""", unsafe_allow_html=True)


def draw_system_status(db_ok: bool, is_scanning: bool):
    """Render the system status checklist card."""
    def row(label, status_cls, status_text, icon_key="check-circle"):
        icon = ICONS[icon_key]
        dot_cls = "dot-green" if status_cls == "ok" else ("dot-amber" if status_cls == "warn" else "dot-grey")
        return f"""
<div style="display:flex;align-items:center;justify-content:space-between;
    padding:7px 0;border-bottom:1px solid var(--border-subtle);">
    <span style="font-size:0.78rem;color:var(--text-secondary);">{label}</span>
    <span style="display:flex;align-items:center;gap:5px;font-size:0.72rem;color:var(--text-muted);">
        <span class="dot {dot_cls}"></span>{status_text}
    </span>
</div>"""

    cam_status = ("ok", "Active") if is_scanning else ("off", "Standby")
    db_status  = ("ok", "Connected") if db_ok else ("warn", "Unavailable")

    rows = (
        row("AI Detection Model", "ok", "Active") +
        row("Camera stream", *cam_status) +
        row("Database", *db_status) +
        row("Network latency", "ok", "— ms")
    )

    st.markdown(f"""
<div class="aegis-card" style="padding:14px 16px;">
    <div class="section-label" style="margin-bottom:6px;">{ICONS['cpu']} System status</div>
    {rows}
</div>
""", unsafe_allow_html=True)


def draw_violation_feed_card(timestamp: str, violation_type: str, worker_id: str,
                              confidence: float, severity: str = "HIGH", status: str = "Violation"):
    """Render a single violation feed item."""
    if status == "Resolved":
        card_cls, badge_html = "v-card v-card-resolved", '<span class="badge badge-safe">Resolved</span>'
    elif severity == "CRITICAL":
        card_cls, badge_html = "v-card v-card-critical", '<span class="badge badge-critical">Critical</span>'
    else:
        card_cls, badge_html = "v-card v-card-high", '<span class="badge badge-high">Warning</span>'

    ts = timestamp.split(" ")[-1] if " " in timestamp else timestamp

    st.markdown(f"""
<div class="{card_cls}">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
        <span class="v-time">{ts}</span>
        {badge_html}
    </div>
    <div class="v-type">{violation_type}</div>
    <div class="v-meta">Worker {worker_id} &nbsp;&#183;&nbsp; Confidence {confidence:.0%}</div>
</div>
""", unsafe_allow_html=True)


# Backward compat alias
def draw_incident_card(timestamp, breach_type, worker_id, confidence, snap_path, status):
    severity = "CRITICAL" if ("Hardhat" in breach_type or "Vest" in breach_type) else "HIGH"
    draw_violation_feed_card(timestamp, breach_type, worker_id, confidence, severity, status)


def section_label(text: str, icon_key: str = ""):
    icon = ICONS.get(icon_key, "") if icon_key else ""
    st.markdown(f'<div class="section-label">{icon} {text}</div>', unsafe_allow_html=True)


def mission_control_header(title: str, subtitle: str):
    """Page-level header for sub-pages."""
    st.markdown(f"""
<div style="margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid var(--border-subtle);">
    <h1 style="font-size:1.5rem;font-weight:800;color:var(--text-primary);
        letter-spacing:-0.3px;margin:0 0 4px 0;">{title}</h1>
    <p style="font-size:0.72rem;color:var(--text-muted);letter-spacing:0.5px;margin:0;">{subtitle}</p>
</div>
""", unsafe_allow_html=True)


def navigation_tip():
    """Compact sidebar nav hint."""
    st.markdown(f"""
<div class="nav-tip">
    <div style="color:rgba(249,168,37,0.7);font-size:0.65rem;font-weight:700;
        text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">Navigation</div>
    <div style="color:rgba(232,237,242,0.4);font-size:0.73rem;line-height:1.5;">
        Safety Monitor &nbsp;&#183;&nbsp; Analytics &nbsp;&#183;&nbsp; Incident Explorer
    </div>
</div>
""", unsafe_allow_html=True)


def render_cctv_hud_header(source_name: str = "CAM-01 • SECTOR NORTH", is_live: bool = False, fps_val: float = 0.0):
    """Render the top metadata bar for the CCTV HUD viewport."""
    live_badge = (
        '<span class="dot dot-live" style="margin-right:6px;"></span>'
        '<span class="cctv-live-tag">LIVE FEED</span>'
    ) if is_live else (
        '<span class="dot dot-grey" style="margin-right:6px;"></span>'
        '<span style="color:var(--text-muted);font-weight:600;font-size:0.68rem;">STANDBY</span>'
    )
    fps_badge = (
        f'<span style="color:var(--accent);font-weight:700;">{fps_val:.1f} FPS</span>'
    ) if (is_live and fps_val > 0) else '<span style="color:var(--text-muted);">0.0 FPS</span>'

    st.markdown(f"""
<div class="cctv-hud-header">
    <div style="display:flex;align-items:center;gap:10px;">
        {live_badge}
        <span style="opacity:0.35;">|</span>
        <span style="font-weight:600;color:var(--text-primary);">{source_name}</span>
    </div>
    <div class="cctv-meta">
        <span>YOLOv8s • AI GUARD</span>
        <span style="opacity:0.35;">|</span>
        {fps_badge}
    </div>
</div>
""", unsafe_allow_html=True)


def standby_placeholder(db_ok: bool = True):

    """Rich standby screen — not an empty black box."""
    db_status = "Connected" if db_ok else "Unavailable"
    db_dot    = "dot-green" if db_ok else "dot-amber"

    st.markdown(f"""
<div class="video-standby">
    <div class="video-standby-icon">
        {ICONS['camera'].replace('16','24').replace('16','24')}
    </div>
    <div class="video-standby-title">Awaiting live video</div>
    <div class="video-standby-sub">
        Start a scan to begin real-time safety monitoring with AI-powered PPE detection.
    </div>
    <div>
        <div class="ready-indicator">
            <span class="dot dot-green"></span>
            <span>Camera ready</span>
        </div>
        <div class="ready-indicator">
            <span class="dot dot-green"></span>
            <span>Detection engine ready</span>
        </div>
        <div class="ready-indicator">
            <span class="dot {db_dot}"></span>
            <span>Database {db_status}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


def scan_complete_placeholder(violations: int, frames: int, duration: str = ""):
    """Post-scan completion state."""
    score = max(0, round((1 - violations / max(frames, 1)) * 100, 1)) if frames > 0 else 100.0
    score_color = "#4CAF50" if score >= 80 else ("#F9A825" if score >= 50 else "#D32F2F")

    st.markdown(f"""
<div class="scan-complete">
    <div style="width:44px;height:44px;background:rgba(46,125,50,0.1);
        border:1.5px solid rgba(46,125,50,0.25);border-radius:50%;
        display:flex;align-items:center;justify-content:center;
        margin:0 auto 14px;color:#4CAF50;">
        {ICONS['check-circle'].replace('16','22')}
    </div>
    <div style="font-size:0.95rem;font-weight:700;color:var(--text-primary);margin-bottom:4px;">Scan session complete</div>
    <div style="width:32px;height:2px;background:linear-gradient(90deg,#2E7D32,#00838F);
        margin:0 auto 12px;border-radius:2px;"></div>
    <p style="color:var(--text-secondary);font-size:0.8rem;max-width:380px;line-height:1.7;margin:0 auto 10px;">
        <b style="color:#81C784;">{violations} unique violations</b> logged across
        <b style="color:#80DEEA;">{frames} frames</b>
        {f'<span style="color:var(--text-muted);"> in {duration}</span>' if duration else ''}.
    </p>
    <div style="font-size:1.4rem;font-weight:700;color:{score_color};">{score}% <span style="font-size:0.78rem;font-weight:500;color:var(--text-muted);">safety score</span></div>
</div>
""", unsafe_allow_html=True)


def render_authenticated_nav(current_page: str = "Live Monitor", user_info: dict = None):
    """
    Render top-level executive navigation bar for authenticated users.
    Displays user profile chip, active status, theme toggle, and Sign Out button.
    """
    user_info = user_info or {}
    name = user_info.get("full_name", "Safety Inspector")
    role = user_info.get("role", "Inspector")
    initials = "".join(part[0].upper() for part in name.split()[:2]) if name else "AI"

    c_brand, c_pill, c_user, c_actions = st.columns([4, 3, 3, 2])

    with c_brand:
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;">
    <div style="width:34px;height:34px;background:rgba(245,158,11,0.12);
        border:1.5px solid rgba(245,158,11,0.3);border-radius:9px;
        display:flex;align-items:center;justify-content:center;color:#F59E0B;flex-shrink:0;">
        {ICONS['shield']}
    </div>
    <div>
        <div style="font-size:0.95rem;font-weight:800;letter-spacing:1px;color:var(--text-primary);">AEGIS SAFETY</div>
        <div style="font-size:0.62rem;color:var(--text-muted);letter-spacing:0.5px;">COMMAND CENTER</div>
    </div>
</div>
""", unsafe_allow_html=True)

    with c_pill:
        st.markdown(f"""
<div style="display:inline-flex;align-items:center;gap:8px;padding:6px 14px;background:var(--bg-card-2);
    border:1px solid var(--border-subtle);border-radius:9999px;margin-top:2px;">
    <span class="dot dot-live"></span>
    <span style="font-size:0.75rem;font-weight:600;color:var(--accent);">{current_page}</span>
</div>
""", unsafe_allow_html=True)

    with c_user:
        st.markdown(f"""
<div class="user-badge-chip">
    <div class="user-avatar">{initials}</div>
    <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
        <div style="font-size:0.78rem;font-weight:700;color:var(--text-primary);">{name}</div>
        <div style="font-size:0.65rem;color:var(--text-muted);">{role}</div>
    </div>
</div>
""", unsafe_allow_html=True)

    with c_actions:
        btn_c1, btn_c2 = st.columns([1, 2])
        with btn_c1:
            render_theme_toggle(key=f"nav_theme_toggle_{current_page.replace(' ', '_')}")
        with btn_c2:
            if st.button("Sign Out", key=f"nav_signout_{current_page.replace(' ', '_')}", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.active_view = "landing"
                st.session_state.running = False
                st.rerun()


def auth_protected_gate(target_page_name: str = "This Page"):
    """
    Renders an access barrier if unauthenticated users access a protected subpage.
    Provides instant action to return to login.
    """
    st.markdown(f"""
<div class="access-gate-card">
    <div style="width:52px;height:52px;background:rgba(239,68,68,0.12);
        border:1.5px solid rgba(239,68,68,0.25);border-radius:50%;
        display:flex;align-items:center;justify-content:center;
        margin:0 auto 18px;color:#EF4444;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
    </div>
    <div style="font-size:1.3rem;font-weight:800;color:var(--text-primary);margin-bottom:8px;">Authentication Required</div>
    <p style="font-size:0.86rem;color:var(--text-secondary);line-height:1.6;margin-bottom:24px;">
        Access to <b>{target_page_name}</b> requires verified credentials with active safety inspector authorization.
    </p>
</div>
""", unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.4, 1])
    with col_m:
        if st.button("🔐 Sign In to Continue", key=f"gate_signin_{target_page_name.replace(' ', '_')}", use_container_width=True):
            st.session_state.active_view = "login"
            st.switch_page("app.py") if hasattr(st, "switch_page") else None
            st.rerun()

