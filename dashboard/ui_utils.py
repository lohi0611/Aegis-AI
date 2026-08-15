"""
AEGIS Safety Intelligence — Premium UI System
Construction Safety Command Center
Dark-first design with light theme support via CSS custom properties.
"""
import streamlit as st

# ── Python colour tokens (for Plotly / Python-side logic only) ────────────────
ORANGE = "#F9A825"   # Safety yellow-amber — primary accent
RED    = "#D32F2F"   # Hazard red
GREEN  = "#2E7D32"   # Safe green (deeper, more industrial)
TEAL   = "#00838F"   # Cyan/teal — technical metrics
BLUE   = "#1565C0"   # Blue — info
AMBER  = "#F57F17"   # Amber

# ── SVG icon library (no emojis) ──────────────────────────────────────────────
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
    "wifi": """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0114.08 0"/><path d="M1.42 9a16 16 0 0121.16 0"/><path d="M8.53 16.11a6 6 0 016.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>""",
    "cpu": """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>""",
    "play": """<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>""",
    "square": """<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>""",
}

# ── Theme definitions ─────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "--bg-base":          "#0B0F14",
        "--bg-sidebar":       "#111720",
        "--bg-card":          "#151B24",
        "--bg-card-2":        "#18202A",
        "--bg-card-3":        "#1B2430",
        "--bg-input":         "rgba(255,255,255,0.04)",
        "--border-subtle":    "rgba(255,255,255,0.07)",
        "--border-medium":    "rgba(255,255,255,0.12)",
        "--border-accent":    "rgba(249,168,37,0.25)",
        "--text-primary":     "#E8EDF2",
        "--text-secondary":   "rgba(232,237,242,0.55)",
        "--text-muted":       "rgba(232,237,242,0.30)",
        "--shadow-card":      "0 1px 3px rgba(0,0,0,0.4), 0 4px 16px rgba(0,0,0,0.3)",
        "--shadow-elevated":  "0 4px 24px rgba(0,0,0,0.5)",
        "--accent-primary":   "#F9A825",
        "--accent-glow":      "rgba(249,168,37,0.12)",
        "--plotly-template":  "plotly_dark",
        "--plotly-paper":     "rgba(0,0,0,0)",
        "--plotly-bg":        "rgba(0,0,0,0)",
        "--plotly-grid":      "rgba(255,255,255,0.05)",
        "--plotly-text":      "rgba(232,237,242,0.4)",
    },
    "light": {
        "--bg-base":          "#F0F4F8",
        "--bg-sidebar":       "#1B2A3B",
        "--bg-card":          "#FFFFFF",
        "--bg-card-2":        "#F8FAFC",
        "--bg-card-3":        "#F1F5F9",
        "--bg-input":         "rgba(0,0,0,0.03)",
        "--border-subtle":    "rgba(0,0,0,0.07)",
        "--border-medium":    "rgba(0,0,0,0.12)",
        "--border-accent":    "rgba(249,168,37,0.35)",
        "--text-primary":     "#0F172A",
        "--text-secondary":   "rgba(15,23,42,0.55)",
        "--text-muted":       "rgba(15,23,42,0.35)",
        "--shadow-card":      "0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.06)",
        "--shadow-elevated":  "0 4px 24px rgba(0,0,0,0.12)",
        "--accent-primary":   "#E65100",
        "--accent-glow":      "rgba(230,81,0,0.08)",
        "--plotly-template":  "plotly_white",
        "--plotly-paper":     "rgba(0,0,0,0)",
        "--plotly-bg":        "rgba(0,0,0,0)",
        "--plotly-grid":      "rgba(0,0,0,0.06)",
        "--plotly-text":      "rgba(15,23,42,0.45)",
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
    --r-sm:         7px;
    --r-lg:         14px;
    --t:            0.18s ease;
}}

/* ── GLOBAL ─────────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background: var(--bg-base) !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased;
}}

/* Subtle radial ambient for dark mode only */
{"[data-testid='stAppViewContainer']::before { content:''; position:fixed; inset:0; background: radial-gradient(ellipse 80% 60% at 10% 0%, rgba(249,168,37,0.05) 0%, transparent 60%), radial-gradient(ellipse 50% 40% at 90% 100%, rgba(0,131,143,0.04) 0%, transparent 55%); pointer-events:none; z-index:0; }" if theme == "dark" else ""}

code, pre {{ font-family: 'JetBrains Mono', 'Fira Code', monospace !important; }}

/* ── HIDE DEFAULT STREAMLIT CLUTTER ─────────────────────────── */
#MainMenu, footer, [data-testid="stDeployButton"] {{ display: none !important; }}
[data-testid="stHeader"] {{ background: transparent !important; height: 0 !important; min-height: 0 !important; }}
[data-testid="collapsedControl"] {{ top: 12px !important; }}
.block-container {{
    padding: 1.25rem 2rem 2rem !important;
    max-width: 1440px !important;
}}

/* ── SIDEBAR ─────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: var(--bg-sidebar) !important;
    border-right: 1px solid rgba(249,168,37,0.1) !important;
    min-width: 260px !important;
    max-width: 280px !important;
}}
section[data-testid="stSidebar"] > div {{ padding: 0 !important; }}
section[data-testid="stSidebar"] label {{
    color: rgba(232,237,242,0.65) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}}
section[data-testid="stSidebar"] p {{ color: rgba(232,237,242,0.55) !important; }}

/* Sidebar section headings */
section[data-testid="stSidebar"] .stMarkdown h3 {{
    color: rgba(249,168,37,0.8) !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.8px !important;
    text-transform: uppercase !important;
    margin: 20px 0 8px !important;
    padding-bottom: 4px !important;
    border-bottom: 1px solid rgba(249,168,37,0.12) !important;
}}

/* ── BUTTONS ─────────────────────────────────────────────────── */
/* Primary / start scan */
.stButton > button {{
    background: #F9A825 !important;
    border: none !important;
    color: #0B0F14 !important;
    border-radius: var(--r-sm) !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.3px !important;
    padding: 10px 20px !important;
    transition: all var(--t) !important;
    box-shadow: 0 2px 12px rgba(249,168,37,0.25) !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    background: #FFB300 !important;
    box-shadow: 0 4px 20px rgba(249,168,37,0.4) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; box-shadow: none !important; }}

/* Stop scan variant */
.stop-btn .stButton > button {{
    background: rgba(211,47,47,0.1) !important;
    border: 1px solid rgba(211,47,47,0.3) !important;
    color: #EF9A9A !important;
    box-shadow: none !important;
    font-weight: 600 !important;
}}
.stop-btn .stButton > button:hover {{
    background: rgba(211,47,47,0.2) !important;
    box-shadow: 0 4px 16px rgba(211,47,47,0.25) !important;
    transform: translateY(-1px) !important;
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
.kpi-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r);
    padding: 16px 18px 18px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-card);
    transition: transform var(--t), box-shadow var(--t), border-color var(--t);
    height: 100%;
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
    top: 16px; bottom: 16px; left: 0;
    width: 3px;
    border-radius: 0 2px 2px 0;
}}
.kpi-yellow::before  {{ background: #F9A825; }}
.kpi-red::before     {{ background: #D32F2F; }}
.kpi-green::before   {{ background: #2E7D32; }}
.kpi-teal::before    {{ background: #00838F; }}
.kpi-blue::before    {{ background: #1565C0; }}
.kpi-orange::before  {{ background: #E65100; }}

.kpi-header {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 10px;
    gap: 8px;
}}
.kpi-label {{
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-secondary);
    line-height: 1.3;
    letter-spacing: 0.1px;
}}
.kpi-icon {{
    color: var(--text-muted);
    flex-shrink: 0;
    margin-top: 1px;
}}
.kpi-value {{
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
    letter-spacing: -0.5px;
}}
.kpi-value-sm {{
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
    word-break: break-word;
}}
.kpi-sub {{
    font-size: 0.68rem;
    color: var(--text-muted);
    margin-top: 4px;
}}

/* ── AEGIS CARD ─────────────────────────────────────────────── */
.aegis-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r);
    padding: 18px 20px;
    box-shadow: var(--shadow-card);
    transition: border-color var(--t);
}}

/* ── SECTION LABEL ──────────────────────────────────────────── */
.section-label {{
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 7px;
}}
.section-label svg {{ opacity: 0.5; }}
.section-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border-subtle);
    margin-left: 4px;
}}

/* ── VIOLATION FEED ─────────────────────────────────────────── */
.v-card {{
    background: var(--bg-card-2);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid #D32F2F;
    border-radius: var(--r-sm);
    padding: 10px 14px;
    margin-bottom: 7px;
    transition: border-color var(--t);
}}
.v-card-critical {{ border-left-color: #D32F2F; }}
.v-card-high     {{ border-left-color: #F57F17; border-left-color: #E65100; }}
.v-card-resolved {{ border-left-color: #2E7D32; }}

.v-time {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.67rem;
    color: var(--text-muted);
}}
.v-type {{
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 3px 0;
}}
.v-meta {{
    font-size: 0.7rem;
    color: var(--text-muted);
}}

/* ── STATUS BADGES ──────────────────────────────────────────── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: 20px;
    font-size: 0.63rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    white-space: nowrap;
}}
.badge-critical {{ background: rgba(211,47,47,0.12);  color: #EF9A9A; border: 1px solid rgba(211,47,47,0.3); }}
.badge-high     {{ background: rgba(230,81,0,0.12);   color: #FFAB91; border: 1px solid rgba(230,81,0,0.3); }}
.badge-safe     {{ background: rgba(46,125,50,0.12);  color: #A5D6A7; border: 1px solid rgba(46,125,50,0.3); }}
.badge-info     {{ background: rgba(0,131,143,0.10);  color: #80DEEA; border: 1px solid rgba(0,131,143,0.25); }}
.badge-running  {{ background: rgba(249,168,37,0.12); color: #FFE082; border: 1px solid rgba(249,168,37,0.3); }}

/* ── STATUS DOTS ────────────────────────────────────────────── */
.dot {{ display: inline-block; width: 7px; height: 7px; border-radius: 50%; }}
.dot-green   {{ background: #4CAF50; box-shadow: 0 0 5px rgba(76,175,80,0.5); }}
.dot-amber   {{ background: #FFC107; box-shadow: 0 0 5px rgba(255,193,7,0.5); }}
.dot-red     {{ background: #F44336; box-shadow: 0 0 5px rgba(244,67,54,0.5); }}
.dot-grey    {{ background: rgba(232,237,242,0.25); }}
.dot-live    {{ background: #F9A825; animation: pulse-dot 1.5s infinite; box-shadow: 0 0 6px rgba(249,168,37,0.6); }}
@keyframes pulse-dot {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%       {{ opacity: 0.5; transform: scale(0.8); }}
}}

/* ── BRAND HEADER ───────────────────────────────────────────── */
.brand-header {{
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-top: 2px solid #F9A825;
    border-radius: var(--r);
    padding: 14px 20px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow-card);
}}
.brand-title {{
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: 2px;
    line-height: 1;
}}
.brand-sub {{
    font-size: 0.67rem;
    color: var(--text-muted);
    letter-spacing: 0.3px;
    margin-top: 3px;
}}
.brand-right {{
    display: flex;
    align-items: center;
    gap: 16px;
}}
.header-status {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    color: var(--text-secondary);
}}

/* ── SITE STATUS PANELS ─────────────────────────────────────── */
.status-panel {{
    border-radius: var(--r);
    padding: 16px 18px;
    text-align: center;
    border: 1px solid;
}}
.status-safe     {{ background: rgba(46,125,50,0.08);  border-color: rgba(46,125,50,0.25); }}
.status-warning  {{ background: rgba(249,168,37,0.08); border-color: rgba(249,168,37,0.25); }}
.status-critical {{
    background: rgba(211,47,47,0.10);
    border-color: rgba(211,47,47,0.3);
    animation: pulse-border 2s infinite;
}}
@keyframes pulse-border {{
    0%, 100% {{ border-color: rgba(211,47,47,0.3); }}
    50%       {{ border-color: rgba(211,47,47,0.6); }}
}}

/* ── VIDEO AREA ─────────────────────────────────────────────── */
.video-standby {{
    background: var(--bg-card-2);
    border: 1px solid var(--border-subtle);
    border-radius: var(--r);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 320px;
    padding: 48px 24px;
    text-align: center;
}}
.video-standby-icon {{
    width: 52px; height: 52px;
    border-radius: 50%;
    background: var(--accent-glow);
    border: 1.5px solid rgba(249,168,37,0.2);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 16px;
    color: #F9A825;
}}
.video-standby-title {{
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 6px;
}}
.video-standby-sub {{
    font-size: 0.78rem;
    color: var(--text-muted);
    max-width: 280px;
    line-height: 1.6;
    margin: 0 auto 20px;
}}
.ready-indicator {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin: 3px 0;
    justify-content: center;
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

/* ── SCROLLBAR ──────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(249,168,37,0.2); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: rgba(249,168,37,0.4); }}

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
