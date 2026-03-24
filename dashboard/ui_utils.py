import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Root styling */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0e14;
        color: #e0e0e0;
    }

    /* Sidebar enhancement */
    section[data-testid="stSidebar"] {
        background-color: #12161f !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #4a90e2 !important;
        font-size: 1.1rem;
        margin-top: 20px;
    }

    /* Modern Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: #4a90e2;
        background: rgba(255, 255, 255, 0.05);
    }

    /* Header styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #4a90e2, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    .subtitle {
        color: rgba(255, 255, 255, 0.5);
        font-size: 1rem;
        margin-bottom: 30px;
    }

    /* UI elements */
    .stButton>button {
        background: rgba(74, 144, 226, 0.1) !important;
        border: 1px solid #4a90e2 !important;
        color: #4a90e2 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }
    .stButton>button:hover {
        background: #4a90e2 !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(74, 144, 226, 0.4);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #4a90e2 !important;
        font-weight: 800 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

def mission_control_header(title, subtitle):
    st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)

def kpi_card(label, value, icon="🔹", color="#4a90e2"):
    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span style="font-size: 1.4rem; color: {color};">{icon}</span>
            <span style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; color: rgba(255,255,255,0.6);">{label}</span>
        </div>
        <div style="font-size: 2.4rem; font-weight: 800; color: #ffffff;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def navigation_tip():
    st.markdown("""
    <div style="padding: 15px; border-radius: 10px; background: rgba(74, 144, 226, 0.05); border-left: 4px solid #4a90e2; margin: 20px 0;">
        <span style="color: #4a90e2; font-weight: 700;">💡 OPERATION PRO-TIP:</span>
        <span style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-left: 10px;">
            Use the <b>Intelligence Hub</b> (Compliance Stats) to view long-term behavioral trends and risk heatmaps.
        </span>
    </div>
    """, unsafe_allow_html=True)
