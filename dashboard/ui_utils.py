import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    /* Global Background and Fonts */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Outfit', sans-serif !important;
        background-color: #06090f !important;
        color: #d1d5db !important;
    }
    
    /* Code elements */
    code, pre, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(74, 144, 226, 0.15) !important;
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.5);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #58a6ff !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 25px;
        letter-spacing: 0.5px;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #06090f;
    }
    ::-webkit-scrollbar-thumb {
        background: #1f2937;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #374151;
    }

    /* Streamlit Components Overrides */
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, rgba(74, 144, 226, 0.15), rgba(0, 212, 255, 0.05)) !important;
        border: 1px solid rgba(88, 166, 255, 0.4) !important;
        color: #58a6ff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 10px 18px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #58a6ff, #00d4ff) !important;
        color: #06090f !important;
        border-color: transparent !important;
        box-shadow: 0 0 20px rgba(88, 166, 255, 0.45) !important;
        transform: translateY(-1px);
    }
    .stButton>button:active {
        transform: translateY(1px);
    }

    /* Custom red buttons (e.g. Stop Scan) if they contain "STOP" or "⏹" */
    div.element-container:has(button:contains("STOP")), div.element-container:has(button:contains("⏹")) button {
        border-color: rgba(248, 81, 73, 0.4) !important;
        color: #f85149 !important;
    }
    div.element-container:has(button:contains("STOP")), div.element-container:has(button:contains("⏹")) button:hover {
        background: linear-gradient(135deg, #f85149, #ff7b72) !important;
        color: #06090f !important;
        box-shadow: 0 0 20px rgba(248, 81, 73, 0.45) !important;
    }

    /* Form controls (Selectbox, Slider, Uploaders) */
    div[data-baseweb="select"] > div {
        background-color: #0d131f !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    div[data-baseweb="select"]:hover > div {
        border-color: rgba(88, 166, 255, 0.5) !important;
    }
    
    /* Sliders styling */
    .stSlider [data-testid="stTickBar"] {
        display: none !important;
    }
    .stSlider > div [data-baseweb="slider"] > div {
        background: #1f2937 !important;
    }
    .stSlider > div [data-baseweb="slider"] > div > div {
        background: linear-gradient(90deg, #58a6ff, #00d4ff) !important;
    }
    .stSlider [data-testid="thumbValue"] {
        color: #58a6ff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600;
    }

    /* Expanders & Dataframe */
    .stExpander {
        background: rgba(13, 19, 31, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        margin-bottom: 15px;
    }
    
    /* Checkbox & Radio styling */
    .stCheckbox [data-testid="stWidgetLabel"] p {
        color: #d1d5db !important;
        font-size: 0.95rem;
    }
    .stCheckbox [role="checkbox"] {
        background-color: #0d131f !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: rgba(13, 19, 31, 0.4) !important;
        border: 1px dashed rgba(88, 166, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }

    /* Modern Glass Cards */
    .glass-card {
        background: rgba(13, 19, 31, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    }
    .glass-card:hover {
        border-color: rgba(88, 166, 255, 0.3);
        background: rgba(13, 19, 31, 0.75);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), 0 0 15px rgba(88, 166, 255, 0.05);
        transform: translateY(-2px);
    }
    
    .glass-card-danger {
        background: rgba(20, 10, 15, 0.7) !important;
        border: 1px solid rgba(248, 81, 73, 0.15) !important;
    }
    .glass-card-danger:hover {
        border-color: rgba(248, 81, 73, 0.45) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), 0 0 15px rgba(248, 81, 73, 0.08) !important;
        transform: translateY(-2px);
    }
    
    .glass-card-success {
        background: rgba(10, 20, 15, 0.7) !important;
        border: 1px solid rgba(46, 160, 67, 0.15) !important;
    }
    
    /* Glowing status indicators */
    .glowing-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    .glowing-badge-danger {
        background: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.3);
        box-shadow: 0 0 10px rgba(248, 81, 73, 0.15);
    }
    
    .glowing-badge-success {
        background: rgba(46, 160, 67, 0.15);
        color: #56d364;
        border: 1px solid rgba(46, 160, 67, 0.3);
        box-shadow: 0 0 10px rgba(46, 160, 67, 0.15);
    }
    
    .glowing-badge-warning {
        background: rgba(210, 153, 34, 0.15);
        color: #e3b341;
        border: 1px solid rgba(210, 153, 34, 0.3);
        box-shadow: 0 0 10px rgba(210, 153, 34, 0.15);
    }

    /* Tech Header Styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #58a6ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }
    .subtitle {
        color: rgba(209, 213, 219, 0.45);
        font-size: 0.95rem;
        margin-bottom: 25px;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Table override */
    [data-testid="stTable"] table {
        background-color: #0d131f !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 8px;
    }
    [data-testid="stTable"] th {
        background-color: #161f30 !important;
        color: #58a6ff !important;
    }
    
    /* Block container alignment */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def mission_control_header(title, subtitle):
    st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)

def kpi_card(label, value, icon="🔹", color="#58a6ff", alert_type=None):
    card_class = "glass-card"
    if alert_type == "danger":
        card_class += " glass-card-danger"
        color = "#f85149"
    elif alert_type == "success":
        card_class += " glass-card-success"
        color = "#56d364"
        
    st.markdown(f"""
    <div class="{card_class}">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: rgba(255,255,255,0.45);">{label}</span>
            <span style="font-size: 1.3rem; color: {color}; filter: drop-shadow(0 0 5px {color}40);">{icon}</span>
        </div>
        <div style="font-size: 2.1rem; font-weight: 800; color: #ffffff; font-family: 'Outfit', sans-serif;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def draw_incident_card(timestamp, breach_type, worker_id, confidence, snap_path, status):
    status_badge = ""
    if status == "Violation":
        status_badge = '<span class="glowing-badge glowing-badge-danger">🚨 Breached</span>'
    elif status == "Resolved":
        status_badge = '<span class="glowing-badge glowing-badge-success">✅ Resolved</span>'
    else:
        status_badge = f'<span class="glowing-badge glowing-badge-warning">⏳ {status}</span>'
        
    st.markdown(f"""
    <div class="glass-card glass-card-danger" style="padding: 15px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: rgba(255,255,255,0.4);">{timestamp}</span>
            {status_badge}
        </div>
        <div style="font-size: 0.95rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">{breach_type}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: rgba(255,255,255,0.65);">
            <span>ID: <b style="color:#58a6ff;">{worker_id}</b></span>
            <span>Conf: <b style="color:#00d4ff; font-family: 'JetBrains Mono';">{confidence:.2f}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def navigation_tip():
    st.markdown("""
    <div style="padding: 16px; border-radius: 12px; background: rgba(88, 166, 255, 0.05); border: 1px solid rgba(88, 166, 255, 0.15); margin: 20px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="font-size: 1.1rem; color: #58a6ff;">📡</span>
            <span style="color: #58a6ff; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.2px;">System Insight</span>
        </div>
        <div style="color: rgba(209, 213, 219, 0.7); font-size: 0.85rem; line-height: 1.4;">
            Switch to the <b>Strategic Analytics Hub</b> in the sidebar to visualize historical compliance metrics and peak violation hours.
        </div>
    </div>
    """, unsafe_allow_html=True)
