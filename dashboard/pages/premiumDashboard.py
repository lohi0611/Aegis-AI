import os
import time
import tempfile
from collections import deque
from datetime import datetime

import streamlit as st
import cv2
import numpy as np
import pandas as pd
from detect import PPEDetector

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="AegisAI PPE Monitoring",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== PREMIUM CSS =====================
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0b0e14;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #12161f !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    
    .sidebar-header i {
        margin-right: 10px;
        color: #4a90e2;
    }

    /* Button Styling */
    .stButton>button {
        background: rgba(255, 255, 255, 0.05);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        width: 100%;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: #4a90e2;
    }

    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    .subtitle {
        color: rgba(255, 255, 255, 0.6);
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    
    .highlight {
        color: white;
        font-weight: 700;
    }

    /* Slider Styling */
    .stSlider > div [data-baseweb="slider"] > div {
        background: #ff4b4b;
    }

    /* Intelligence Feed */
    .feed-container {
        border-left: 2px solid rgba(255, 255, 255, 0.05);
        padding-left: 20px;
        height: 60vh;
        overflow-y: auto;
    }
    
    .feed-title {
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 20px;
    }

    /* Footer Stats */
    .footer-stats {
        position: fixed;
        bottom: 10px;
        right: 20px;
        display: flex;
        gap: 20px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.4);
    }
    
    .status-value {
        color: #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown('<div class="sidebar-header">🛡️ AegisAI Operation</div>', unsafe_allow_html=True)
    st.markdown("*Tactical Command Interface*")
    
    st.markdown("---")
    
    st.markdown("### 📡 Sensor Configuration")
    video_source = st.selectbox("Intelligence Source", ["Webcam (0)", "Video File", "RTSP Stream"])
    
    confidence = st.slider("Neural Threshold", 0.0, 1.0, 0.50, step=0.01)
    st.markdown(f'<p style="color:#ff4b4b; font-size:0.8rem; margin-top:-15px;">Sensitivity Level: {confidence:.2f}</p>', unsafe_allow_html=True)
    
    uploaded_file = None
    if video_source == "Video File":
        uploaded_file = st.file_uploader("Upload Node Feed", type=["mp4", "avi"])
        
    st.markdown("---")
    initialize_scanner = st.checkbox("Active Neural Scanning", value=True)

# ===================== MAIN AREA =====================
st.markdown('<div style="text-align: center; padding: 10px; border-bottom: 2px solid #4a90e2; margin-bottom: 20px;">'
            '<h1 style="margin:0; letter-spacing: 5px;">AEGIS-AI <span style="color:#4a90e2;">COMMAND</span></h1>'
            '<p style="color:rgba(255,255,255,0.5); margin:0;">GLOBAL SAFETY PROTOCOL ACTIVE</p></div>', unsafe_allow_html=True)

col_main, col_feed = st.columns([3, 1.2])

with col_main:
    st.markdown('### 💠 Live Optic Array', unsafe_allow_html=True)
    video_placeholder = st.empty()
    
    # Bottom Stats Simulation
    st.markdown(f"""
    <div class="footer-stats">
        <span>CORE LOAD: <span class="status-value">LOW</span></span>
        <span>LATENCY: <span class="status-value">12MS</span></span>
        <span>NODE: <span class="status-value">FAB-NORTH-PRIM</span></span>
    </div>
    """, unsafe_allow_html=True)

with col_feed:
    st.markdown('<div class="feed-title">INTELLIGENCE FEED</div>', unsafe_allow_html=True)
    feed_placeholder = st.container()

# ===================== DETECTION LOGIC =====================
if initialize_scanner:
    detector = PPEDetector(conf=confidence)
    
    # Initialize session state for logs
    if "premium_logs" not in st.session_state:
        st.session_state.premium_logs = []

    cap = None
    if video_source == "Webcam (0)":
        cap = cv2.VideoCapture(0)
    elif video_source == "Video File" and uploaded_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        
    if cap and cap.isOpened():
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                annotated_frame, detections = detector.detect(rgb_frame)
                
                video_placeholder.image(annotated_frame, use_container_width=True)
                
                # Update Intelligence Feed
                for d in detections:
                    if d["class_name"].startswith("NO-"):
                        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {d['class_name']} DETECTED ({d['confidence']:.2f})"
                        st.session_state.premium_logs.append(log_entry)
                        
                with col_feed:
                    for log in st.session_state.premium_logs[-15:]:
                        st.markdown(f'<p style="font-size:0.8rem; color:#ff4b4b; border-bottom:1px solid rgba(255,255,255,0.05); padding:5px 0;">{log}</p>', unsafe_allow_html=True)
                
                time.sleep(0.01)
        finally:
            cap.release()
    else:
        video_placeholder.info("Waiting for video source...")
else:
    st.info("AI Scanner is disabled.")
