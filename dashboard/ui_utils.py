import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── GLOBAL RESET ── */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"] {
        font-family: 'Inter', system-ui, sans-serif !important;
        background: #060a12 !important;
        color: #e2e8f0 !important;
    }

    /* Animated mesh gradient background */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse 80% 60% at 20% 0%, rgba(56, 97, 251, 0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 10%, rgba(139, 92, 246, 0.08) 0%, transparent 55%),
            radial-gradient(ellipse 50% 40% at 50% 90%, rgba(6, 182, 212, 0.06) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── TYPOGRAPHY ── */
    code, pre { font-family: 'JetBrains Mono', monospace !important; }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #0a0e18 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    section[data-testid="stSidebar"] > div { padding: 1rem 0.75rem !important; }

    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #60a5fa !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        margin: 20px 0 8px !important;
        padding-bottom: 6px !important;
        border-bottom: 1px solid rgba(96,165,250,0.15) !important;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: 1px solid rgba(96,165,250,0.3) !important;
        color: #fff !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.3px !important;
        padding: 9px 18px !important;
        transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
        box-shadow: 0 2px 12px rgba(37,99,235,0.25) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        box-shadow: 0 4px 20px rgba(59,130,246,0.45) !important;
        transform: translateY(-1px) !important;
        border-color: rgba(96,165,250,0.6) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── FORM CONTROLS ── */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        transition: border-color 0.2s !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: rgba(96,165,250,0.4) !important;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: rgba(96,165,250,0.6) !important;
        box-shadow: 0 0 0 3px rgba(96,165,250,0.1) !important;
    }

    /* Slider */
    .stSlider [data-baseweb="slider"] > div { background: rgba(255,255,255,0.08) !important; }
    .stSlider [data-baseweb="slider"] [role="slider"] { background: #3b82f6 !important; box-shadow: 0 0 0 4px rgba(59,130,246,0.2) !important; }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 1px dashed rgba(96,165,250,0.3) !important;
        border-radius: 12px !important;
        background: rgba(59,130,246,0.04) !important;
        padding: 8px !important;
    }

    /* Camera input */
    [data-testid="stCameraInput"] video,
    [data-testid="stCameraInput"] img {
        border-radius: 12px !important;
        border: 1px solid rgba(96,165,250,0.2) !important;
    }

    /* Multiselect tags */
    [data-baseweb="tag"] {
        background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2)) !important;
        border: 1px solid rgba(96,165,250,0.3) !important;
        border-radius: 6px !important;
    }

    /* ── GLASS CARD (base) ── */
    .glass-card {
        position: relative;
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        overflow: hidden;
    }
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96,165,250,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(96,165,250,0.08);
    }

    .glass-card-danger {
        background: linear-gradient(135deg, rgba(239,68,68,0.08) 0%, rgba(239,68,68,0.03) 100%) !important;
        border: 1px solid rgba(239,68,68,0.2) !important;
        box-shadow: 0 4px 24px rgba(239,68,68,0.08) !important;
    }
    .glass-card-danger::before {
        background: linear-gradient(90deg, transparent, rgba(239,68,68,0.2), transparent) !important;
    }

    .glass-card-success {
        background: linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(16,185,129,0.03) 100%) !important;
        border: 1px solid rgba(16,185,129,0.2) !important;
        box-shadow: 0 4px 24px rgba(16,185,129,0.08) !important;
    }
    .glass-card-success::before {
        background: linear-gradient(90deg, transparent, rgba(16,185,129,0.2), transparent) !important;
    }

    /* ── KPI CARD SPECIFIC ── */
    .kpi-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 10px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0; height: 3px;
        border-radius: 0 0 16px 16px;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }
    .kpi-card-blue::after   { background: linear-gradient(90deg, #3b82f6, #60a5fa); box-shadow: 0 0 12px rgba(59,130,246,0.5); }
    .kpi-card-red::after    { background: linear-gradient(90deg, #ef4444, #f87171); box-shadow: 0 0 12px rgba(239,68,68,0.5); }
    .kpi-card-green::after  { background: linear-gradient(90deg, #10b981, #34d399); box-shadow: 0 0 12px rgba(16,185,129,0.5); }
    .kpi-card-cyan::after   { background: linear-gradient(90deg, #06b6d4, #22d3ee); box-shadow: 0 0 12px rgba(6,182,212,0.5); }
    .kpi-card-amber::after  { background: linear-gradient(90deg, #f59e0b, #fbbf24); box-shadow: 0 0 12px rgba(245,158,11,0.5); }

    .kpi-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: rgba(255,255,255,0.4);
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
        letter-spacing: -0.5px;
    }
    .kpi-icon {
        position: absolute;
        top: 16px; right: 18px;
        font-size: 1.5rem;
        opacity: 0.7;
    }

    /* ── BADGES ── */
    .glowing-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        white-space: nowrap;
    }
    .glowing-badge-danger {
        background: rgba(239,68,68,0.12);
        color: #fca5a5;
        border: 1px solid rgba(239,68,68,0.35);
        box-shadow: 0 0 8px rgba(239,68,68,0.15);
    }
    .glowing-badge-success {
        background: rgba(16,185,129,0.12);
        color: #6ee7b7;
        border: 1px solid rgba(16,185,129,0.35);
        box-shadow: 0 0 8px rgba(16,185,129,0.15);
    }
    .glowing-badge-warning {
        background: rgba(245,158,11,0.12);
        color: #fcd34d;
        border: 1px solid rgba(245,158,11,0.35);
        box-shadow: 0 0 8px rgba(245,158,11,0.15);
    }

    /* ── HEADER ── */
    .main-header {
        font-size: 2.4rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -1px;
        line-height: 1.1;
        margin-bottom: 6px;
        background: linear-gradient(135deg, #ffffff 0%, rgba(255,255,255,0.75) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .header-accent {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .subtitle {
        font-size: 0.78rem;
        font-weight: 500;
        color: rgba(255,255,255,0.35);
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 24px;
    }

    /* ── DIVIDERS ── */
    hr { border-color: rgba(255,255,255,0.06) !important; margin: 12px 0 !important; }

    /* ── SECTION HEADINGS ── */
    .section-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: rgba(255,255,255,0.85);
        letter-spacing: 0.3px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.08), transparent);
    }

    /* ── TABLES / DATAFRAMES ── */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* ── INFO / ALERT BOXES ── */
    .stAlert {
        background: rgba(59,130,246,0.08) !important;
        border: 1px solid rgba(59,130,246,0.2) !important;
        border-radius: 12px !important;
        color: #93c5fd !important;
    }

    /* Streamlit Info box */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background: rgba(255,255,255,0.03) !important;
    }

    /* ── BLOCK CONTAINER ── */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }

    /* ── INCIDENT CARD STREAM ── */
    .incident-stream-card {
        background: linear-gradient(135deg, rgba(239,68,68,0.07) 0%, rgba(15,20,35,0.95) 100%);
        border: 1px solid rgba(239,68,68,0.18);
        border-left: 3px solid #ef4444;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        position: relative;
        box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
    ::-webkit-scrollbar-thumb { background: rgba(96,165,250,0.25); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(96,165,250,0.45); }

    /* ── CAMERA WIDGET LABEL ── */
    [data-testid="stCameraInputButton"] button {
        background: linear-gradient(135deg, #1d4ed8, #7c3aed) !important;
        border-radius: 10px !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* Download button */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(6,182,212,0.15)) !important;
        border: 1px solid rgba(16,185,129,0.35) !important;
        color: #6ee7b7 !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        width: 100% !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(6,182,212,0.25)) !important;
        box-shadow: 0 4px 20px rgba(16,185,129,0.25) !important;
    }

    /* Sidebar text input */
    [data-testid="stTextInput"] > div > div > input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stTextInput"] > div > div > input:focus {
        border-color: rgba(96,165,250,0.5) !important;
        box-shadow: 0 0 0 3px rgba(96,165,250,0.1) !important;
    }

    /* Number input */
    [data-testid="stNumberInput"] > div > div > input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        text-align: center !important;
        font-weight: 600 !important;
    }

    /* Toast */
    [data-testid="stToast"] {
        background: rgba(15,20,35,0.95) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(20px) !important;
    }

    /* Date input */
    [data-baseweb="datepicker"] input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }

    </style>
    """, unsafe_allow_html=True)


def mission_control_header(title, subtitle):
    st.markdown(f"""
    <div style="margin-bottom: 8px;">
        <h1 class="main-header" style="-webkit-text-fill-color: unset; background: none; color: #ffffff;">{title}</h1>
        <p class="subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, icon="🔹", color="#3b82f6", alert_type=None):
    color_class = "kpi-card-blue"
    if alert_type == "danger" or color in ("#ef4444", "#f85149"):
        color_class = "kpi-card-red"
    elif alert_type == "success" or color in ("#10b981", "#56d364"):
        color_class = "kpi-card-green"
    elif color in ("#06b6d4", "#00d4ff", "#38bdf8"):
        color_class = "kpi-card-cyan"
    elif color in ("#f59e0b", "#e3b341"):
        color_class = "kpi-card-amber"

    st.markdown(f"""
    <div class="kpi-card {color_class}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def draw_incident_card(timestamp, breach_type, worker_id, confidence, snap_path, status):
    if status == "Violation":
        badge = '<span class="glowing-badge glowing-badge-danger">🚨 Violation</span>'
        border_color = "#ef4444"
    elif status == "Resolved":
        badge = '<span class="glowing-badge glowing-badge-success">✅ Resolved</span>'
        border_color = "#10b981"
    else:
        badge = f'<span class="glowing-badge glowing-badge-warning">⏳ {status}</span>'
        border_color = "#f59e0b"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 3px solid {border_color};
        border-radius: 12px;
        padding: 13px 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.25);
        transition: all 0.2s ease;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:7px;">
            <span style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:rgba(255,255,255,0.35); letter-spacing:0.5px;">{timestamp}</span>
            {badge}
        </div>
        <div style="font-size:0.9rem; font-weight:700; color:#ffffff; margin-bottom:6px; letter-spacing:-0.2px;">{breach_type}</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:0.75rem; color:rgba(255,255,255,0.45);">
                Worker: <b style="color:#60a5fa; font-weight:600;">{worker_id}</b>
            </span>
            <span style="font-size:0.75rem; color:rgba(255,255,255,0.45);">
                Conf: <b style="color:#22d3ee; font-family:'JetBrains Mono',monospace; font-weight:600;">{confidence:.2f}</b>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def navigation_tip():
    st.markdown("""
    <div style="
        padding: 13px 15px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.05));
        border: 1px solid rgba(96,165,250,0.18);
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(59,130,246,0.06);
    ">
        <div style="display:flex; align-items:center; gap:7px; margin-bottom:5px;">
            <span style="font-size:0.85rem;">💡</span>
            <span style="color:#60a5fa; font-weight:700; font-size:0.72rem; text-transform:uppercase; letter-spacing:1px;">Navigation</span>
        </div>
        <div style="color:rgba(255,255,255,0.45); font-size:0.78rem; line-height:1.5;">
            Use the sidebar menu to switch between <b style="color:rgba(255,255,255,0.7);">Safety Control</b>, <b style="color:rgba(255,255,255,0.7);">Analytics</b> &amp; <b style="color:rgba(255,255,255,0.7);">Incident Explorer</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
