import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Background and Fonts */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
        background-color: #0b0f17 !important;
        color: #e2e8f0 !important;
    }
    
    /* Code elements */
    code, pre, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #60a5fa !important;
        font-size: 0.95rem;
        font-weight: 700;
        margin-top: 20px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* Streamlit Buttons Override */
    .stButton>button {
        background: #2563eb !important;
        border: 1px solid #3b82f6 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }
    .stButton>button:hover {
        background: #1d4ed8 !important;
        border-color: #2563eb !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }

    /* Form controls (Selectbox, Slider, Uploaders) */
    div[data-baseweb="select"] > div {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Sliders styling */
    .stSlider > div [data-baseweb="slider"] > div {
        background: #374151 !important;
    }
    .stSlider > div [data-baseweb="slider"] > div > div {
        background: #3b82f6 !important;
    }

    /* Clean Enterprise Cards */
    .glass-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .glass-card:hover {
        border-color: #374151;
    }
    
    .glass-card-danger {
        background: rgba(239, 68, 68, 0.05) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
    }
    
    .glass-card-success {
        background: rgba(16, 185, 129, 0.05) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
    }
    
    /* Glowing status indicators */
    .glowing-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .glowing-badge-danger {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .glowing-badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .glowing-badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    /* Main Header Styling */
    .main-header {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .subtitle {
        color: #9ca3af;
        font-size: 0.875rem;
        margin-bottom: 20px;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    /* Block container alignment */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def mission_control_header(title, subtitle):
    st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)

def kpi_card(label, value, icon="🔹", color="#3b82f6", alert_type=None):
    card_class = "glass-card"
    if alert_type == "danger":
        card_class += " glass-card-danger"
        color = "#ef4444"
    elif alert_type == "success":
        card_class += " glass-card-success"
        color = "#10b981"
        
    st.markdown(f"""
    <div class="{card_class}">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #9ca3af;">{label}</span>
            <span style="font-size: 1.2rem;">{icon}</span>
        </div>
        <div style="font-size: 1.75rem; font-weight: 700; color: #ffffff; font-family: 'Plus Jakarta Sans', sans-serif;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def draw_incident_card(timestamp, breach_type, worker_id, confidence, snap_path, status):
    status_badge = ""
    if status == "Violation":
        status_badge = '<span class="glowing-badge glowing-badge-danger">🚨 Violation</span>'
    elif status == "Resolved":
        status_badge = '<span class="glowing-badge glowing-badge-success">✅ Resolved</span>'
    else:
        status_badge = f'<span class="glowing-badge glowing-badge-warning">⏳ {status}</span>'
        
    st.markdown(f"""
    <div class="glass-card glass-card-danger" style="padding: 14px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9ca3af;">{timestamp}</span>
            {status_badge}
        </div>
        <div style="font-size: 0.9rem; font-weight: 600; color: #ffffff; margin-bottom: 4px;">{breach_type}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #9ca3af;">
            <span>Worker: <b style="color:#60a5fa;">{worker_id}</b></span>
            <span>Conf: <b style="color:#38bdf8; font-family: 'JetBrains Mono';">{confidence:.2f}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def navigation_tip():
    st.markdown("""
    <div style="padding: 14px 16px; border-radius: 8px; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.2); margin: 15px 0;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="font-size: 1rem;">💡</span>
            <span style="color: #60a5fa; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">Navigation Tip</span>
        </div>
        <div style="color: #9ca3af; font-size: 0.825rem; line-height: 1.4;">
            Use the sidebar menu to navigate between <b>Safety Control</b>, <b>Analytics</b>, and <b>Incident Explorer</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
