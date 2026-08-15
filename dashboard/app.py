import os
import time
import csv
import tempfile
import random
from collections import deque
from datetime import datetime

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Intelligence & UI Utils
from ui_utils import apply_custom_css, mission_control_header, kpi_card, draw_incident_card, navigation_tip
from detect import PPEDetector
import streamlit.components.v1 as components

# ===================== CENTROID TRACKER FOR DEDUPLICATION =====================
class CentroidTracker:
    def __init__(self, max_disappeared=15, min_distance=100):
        self.next_id = 101
        self.objects = {} # w_id -> centroid (cx, cy)
        self.disappeared = {} # w_id -> frame_count
        self.classes = {} # w_id -> class_name
        self.logged_violations = {} # (w_id, class_name) -> timestamp
        self.max_disappeared = max_disappeared
        self.min_distance = min_distance

    def register(self, centroid, class_name):
        w_id = f"WKR_{self.next_id}"
        self.objects[w_id] = centroid
        self.disappeared[w_id] = 0
        self.classes[w_id] = class_name
        self.next_id += 1
        return w_id

    def deregister(self, w_id):
        if w_id in self.objects:
            del self.objects[w_id]
        if w_id in self.disappeared:
            del self.disappeared[w_id]
        if w_id in self.classes:
            del self.classes[w_id]

    def update(self, rects, class_names):
        if len(rects) == 0:
            for w_id in list(self.disappeared.keys()):
                self.disappeared[w_id] += 1
                if self.disappeared[w_id] > self.max_disappeared:
                    self.deregister(w_id)
            return []

        input_centroids = []
        for (x1, y1, x2, y2) in rects:
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            input_centroids.append((cx, cy))

        if len(self.objects) == 0:
            assigned_ids = []
            for i in range(len(input_centroids)):
                w_id = self.register(input_centroids[i], class_names[i])
                assigned_ids.append(w_id)
            return assigned_ids

        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        assigned_ids = [None] * len(input_centroids)
        used_objs = set()

        for i, (icx, icy) in enumerate(input_centroids):
            best_dist = float('inf')
            best_id = None
            for j, w_id in enumerate(object_ids):
                if w_id in used_objs:
                    continue
                if self.classes[w_id] != class_names[i]:
                    continue
                ocx, ocy = object_centroids[j]
                dist = ((icx - ocx)**2 + (icy - ocy)**2)**0.5
                if dist < best_dist and dist < self.min_distance:
                    best_dist = dist
                    best_id = w_id
            
            if best_id is not None:
                self.objects[best_id] = (icx, icy)
                self.disappeared[best_id] = 0
                assigned_ids[i] = best_id
                used_objs.add(best_id)
            else:
                w_id = self.register((icx, icy), class_names[i])
                assigned_ids[i] = w_id

        for w_id in object_ids:
            if w_id not in used_objs:
                self.disappeared[w_id] += 1
                if self.disappeared[w_id] > self.max_disappeared:
                    self.deregister(w_id)

        return assigned_ids

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="AegisAI | Safety Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Premium Styling
apply_custom_css()

# ===================== ABSOLUTE PATH RESOLUTION =====================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Ensure LOG_CSV resolves to project root violations.csv
def resolve_log_csv():
    candidates = [
        os.path.join(project_root, "violations.csv"),
        os.path.join(current_dir, "violations.csv"),
        "violations.csv"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return os.path.join(project_root, "violations.csv")

LOG_CSV = resolve_log_csv()
SNAP_DIR = os.path.join(project_root, "snapshots")
os.makedirs(SNAP_DIR, exist_ok=True)

# Declare Custom Auto Camera Component
component_dir = os.path.join(current_dir, "camera_component")
auto_camera = components.declare_component("auto_camera", path=component_dir)

# Find Sample Video
sample_video_paths = [
    os.path.join(current_dir, "uploaded_video.mp4"),
    os.path.join(project_root, "uploaded_video.mp4"),
    os.path.join(project_root, "assets", "finalTest.mp4"),
    os.path.join(project_root, "infosys", "dataset", "source_files", "source_files", "hardhat.mp4"),
    os.path.join(project_root, "infosys", "dataset", "source_files", "source_files", "JapanPPE.mp4"),
]
sample_video = None
for p in sample_video_paths:
    if os.path.exists(p):
        sample_video = p
        break

VIOLATION_CLASSES = ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
ALL_CLASSES = ["Hardhat", "Mask", "NO-Hardhat", "NO-Mask", "NO-Safety Vest", "Person", "Safety Cone", "Safety Vest", "Machinery", "Vehicle"]
CSV_HEADER = ["timestamp", "worker_id", "violation_type", "confidence", "x1", "y1", "x2", "y2", "snapshot_path", "status"]

# Ensure CSV header exists
if not os.path.isfile(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px;">
        <div style="font-size:2.4rem; margin-bottom:8px; filter: drop-shadow(0 0 16px rgba(59,130,246,0.5));">🛡️</div>
        <div style="font-size:1.05rem; font-weight:800; color:#ffffff; letter-spacing:1.5px;">AEGIS AI</div>
        <div style="font-size:0.65rem; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:2px; margin-top:3px;">Safety Intelligence Platform</div>
    </div>
    <div style="height:1px; background:linear-gradient(90deg, transparent, rgba(96,165,250,0.2), transparent); margin: 10px 0 16px;"></div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ CONFIGURATION")
    
    # Input Sources
    sources = ["Laptop Camera (Browser)"]
    if sample_video:
        sources.append("Sample Video")
    sources.extend(["Upload Video File", "Local Webcam (OpenCV)"])
    
    video_source = st.selectbox("Video Input Source", sources)
    
    confidence_slider = st.slider("Detection Confidence Threshold", 0.1, 1.0, 0.25, step=0.01)
    line_thickness = st.slider("Bounding Box Thickness", 1, 5, 2)
    
    alert_classes = st.multiselect(
        "Violations To Monitor",
        options=VIOLATION_CLASSES,
        default=VIOLATION_CLASSES
    )
    
    uploaded_file = None
    if video_source == "Upload Video File":
        uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov"])
    
    use_dshow = st.checkbox("Enhanced Hardware Access", value=True)
    
    st.markdown("---")
    st.markdown("### 🎮 CONTROL PANEL")
    
    if "running" not in st.session_state: 
        st.session_state.running = False
    if "session_rows" not in st.session_state:
        st.session_state.session_rows = []
    if "total_frames_scanned" not in st.session_state:
        st.session_state.total_frames_scanned = 0
    if "fps_history" not in st.session_state:
        st.session_state.fps_history = []
    if "time_history" not in st.session_state:
        st.session_state.time_history = []
    if "current_run_id" not in st.session_state:
        st.session_state.current_run_id = 0

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        start_btn = st.button("▶ START SCAN")
    with col_c2:
        stop_btn = st.button("⏹ STOP SCAN")
        
    if start_btn:
        st.session_state.running = True
        st.session_state.session_rows = []
        st.session_state.total_frames_scanned = 0
        st.session_state.fps_history = []
        st.session_state.time_history = []
        st.session_state.current_run_id += 1
        st.session_state.tracker = CentroidTracker()
    if stop_btn:
        st.session_state.running = False

    navigation_tip()

# ===================== MAIN HEADER =====================
mission_control_header(
    "AEGIS <span style='background:linear-gradient(135deg,#3b82f6,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'>AI SAFETY</span> CONTROL",
    "REAL-TIME PPE COMPLIANCE SURVEILLANCE & INCIDENT MONITORING"
)

# ===================== KPI BANNER =====================
col_k1, col_k2, col_k3, col_k4 = st.columns(4)

# Helper to load stats dynamically
def draw_current_kpis(scanned=None, breaches=None, status=None, latency=None):
    if scanned is None:
        scanned = st.session_state.get("total_frames_scanned", 0)
    if breaches is None:
        breaches = len(st.session_state.get("session_rows", []))
    if status is None:
        if breaches > 0:
            status = f"{breaches} BREACHES"
            alert_t = "danger"
            color = "#ef4444"
        else:
            status = "SECURE"
            alert_t = "success"
            color = "#10b981"
    else:
        alert_t = "danger" if "BREACH" in status else "success" if status == "SECURE" else None
        color = "#ef4444" if alert_t == "danger" else "#10b981" if alert_t == "success" else "#06b6d4"

    if latency is None:
        fps_hist = st.session_state.get("fps_history", [])
        if fps_hist:
            avg_fps = sum(fps_hist) / len(fps_hist)
            latency = f"{avg_fps:.1f} FPS"
        else:
            latency = "STANDBY"
    
    with col_k1: kpi_card("Scanned Frames", str(scanned), "👁️", "#3b82f6")
    with col_k2: kpi_card("Total Breaches", str(breaches), "🚨", "#ef4444")
    with col_k3: kpi_card("Current Threat Level", status, "🛡️" if status == "SECURE" else "🔥", color, alert_type=alert_t)
    with col_k4: kpi_card("Sensor Latency", latency, "⚡", "#06b6d4")

# Helper to load initial default stats
def draw_empty_kpis():
    draw_current_kpis(scanned=0, breaches=0, status="SECURE", latency="STANDBY")

st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

# ===================== MONITORING GRID =====================
col_left, col_right = st.columns([2.5, 1.2])

with col_left:
    st.markdown('<div class="section-title">📹 Live Feed Stream</div>', unsafe_allow_html=True)
    video_ph = st.empty()

with col_right:
    st.markdown('<div class="section-title">🚨 Recent Alerts</div>', unsafe_allow_html=True)
    feed_ph = st.container()

# ===================== CHICKLET FEED & LOGS =====================
st.markdown("---")
c_metrics, c_logs = st.columns([1.5, 2.2])

with c_metrics:
    st.markdown('<div class="section-title">📈 Stream Performance</div>', unsafe_allow_html=True)
    metrics_chart_ph = st.empty()

with c_logs:
    st.markdown('<div class="section-title">📋 Real-time Audit Log</div>', unsafe_allow_html=True)
    logs_ph = st.empty()

# Initialize dataframes & chart placeholders
def draw_empty_metrics():
    fig = go.Figure()
    fig.update_layout(
        height=180, margin=dict(l=10, r=10, t=10, b=10),
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, title="FPS")
    )
    metrics_chart_ph.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="empty_metrics_chart")
    logs_ph.info("Awaiting sensor stream activation...")


# ===================== DETECTION ENGINE =====================
if video_source == "Laptop Camera (Browser)":
    if st.session_state.running:
        detector = PPEDetector(conf=confidence_slider)
        
        # Load the custom camera component
        val = auto_camera(key="auto_camera_key")
        
        if not val:
            video_ph.info("📷 Connecting to camera... Please allow camera access in your browser.")
            
        elif isinstance(val, str) and val.startswith("ERROR:"):
            st.error(f"Webcam Error: {val}")
            st.session_state.running = False
            st.rerun()
            
        elif isinstance(val, str) and val.startswith("data:image/jpeg;base64,"):
            # Decode base64 image
            header, encoded = val.split(",", 1)
            import base64
            img_data = base64.b64decode(encoded)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            st.session_state.total_frames_scanned += 1
            
            # Detect (drawing violations directly on frame)
            annotated, detections = detector.detect(frame, line_width=line_thickness, alert_classes=alert_classes)
            
            # Centroid tracking & deduplication
            rects = [d["bbox"] for d in detections]
            class_names = [d["class_name"] for d in detections]
            
            if "tracker" not in st.session_state or st.session_state.tracker is None:
                st.session_state.tracker = CentroidTracker()
            tracker = st.session_state.tracker
            
            assigned_ids = tracker.update(rects, class_names)
            
            frame_violations = 0
            rows_to_save = []
            
            for idx, d in enumerate(detections):
                cls_name = d["class_name"]
                if cls_name in alert_classes:
                    frame_violations += 1
                    w_id = assigned_ids[idx] if idx < len(assigned_ids) else "Unknown"
                    
                    # Cooldown deduplication per worker/violation class (15 sec interval)
                    now_ts = time.time()
                    log_key = (w_id, cls_name)
                    if log_key not in tracker.logged_violations or (now_ts - tracker.logged_violations[log_key]) > 15.0:
                        tracker.logged_violations[log_key] = now_ts
                        
                        ts_raw = datetime.now()
                        ts_str = ts_raw.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Save Snap
                        snap_id = f"snap_{ts_raw.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                        snap_path = os.path.join("snapshots", snap_id)
                        abs_snap_path = os.path.join(SNAP_DIR, snap_id)
                        cv2.imwrite(abs_snap_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
                        
                        row = [ts_str, w_id, cls_name, d["confidence"], 
                               int(d["bbox"][0]), int(d["bbox"][1]), int(d["bbox"][2]), int(d["bbox"][3]), 
                               snap_path, "Violation"]
                        rows_to_save.append(row)
                        st.session_state.session_rows.append(row)
            
            if rows_to_save:
                with open(LOG_CSV, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(rows_to_save)
            
            # Performance timing
            if "prev_time" not in st.session_state:
                st.session_state.prev_time = time.time()
            now = time.time()
            fps = 1.0 / max(1e-6, (now - st.session_state.prev_time))
            st.session_state.prev_time = now
            
            st.session_state.fps_history.append(fps)
            if len(st.session_state.fps_history) > 60:
                st.session_state.fps_history.pop(0)
                
            st.session_state.time_history.append(datetime.now().strftime("%H:%M:%S"))
            if len(st.session_state.time_history) > 60:
                st.session_state.time_history.pop(0)
            
            # Display annotated result
            video_ph.image(annotated, channels="BGR", use_container_width=True)
            
            # Update KPIs
            draw_current_kpis(latency=f"{fps:.1f} FPS")
            
            # Performance Chart Update
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(st.session_state.time_history), y=list(st.session_state.fps_history),
                mode='lines', name='FPS', 
                line=dict(color='#58a6ff', width=2),
                fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.08)'
            ))
            fig.update_layout(
                height=180, margin=dict(l=10, r=10, t=10, b=10),
                template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, visible=False),
                yaxis=dict(showgrid=False, title=dict(text="FPS", font=dict(color="#58a6ff")), tickfont=dict(color="#58a6ff"))
            )
            metrics_chart_ph.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"fps_chart_camera_{st.session_state.total_frames_scanned}")
            
            # Feed Update (Incident list)
            with feed_ph:
                if st.session_state.session_rows:
                    recent_logs = st.session_state.session_rows[-4:]
                    for r_log in reversed(recent_logs):
                        draw_incident_card(
                            timestamp=r_log[0].split(" ")[1], 
                            breach_type=r_log[2], 
                            worker_id=r_log[1], 
                            confidence=r_log[3], 
                            snap_path=r_log[8],
                            status=r_log[9]
                        )
                else:
                    st.info("No safety breaches recorded in this session.")
            
            # Table Logs Update
            if st.session_state.session_rows:
                logs_df = pd.DataFrame(st.session_state.session_rows, columns=CSV_HEADER).tail(30)
                logs_ph.dataframe(logs_df[["timestamp", "worker_id", "violation_type", "confidence", "status"]], use_container_width=True)

elif st.session_state.running:
    detector = PPEDetector(conf=confidence_slider)
    
    # Resolve Source path smoothly
    cap_src = None
    if video_source == "Sample Video" and sample_video:
        cap_src = sample_video
    elif video_source == "Upload Video File":
        if uploaded_file:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]).name
            with open(tmp_file, "wb") as f:
                f.write(uploaded_file.read())
            cap_src = tmp_file
        else:
            st.warning("⚠️ Please upload a video file to begin.")
            st.session_state.running = False
            st.stop()
    elif video_source == "Local Webcam (OpenCV)":
        cap_src = 0
    
    # Fallback if source is missing
    if cap_src is None:
        if sample_video:
            cap_src = sample_video
            st.info("ℹ️ Using sample video stream for demonstration.")
        else:
            st.warning("⚠️ Please upload a video file or select a valid video source.")
            st.session_state.running = False
            st.stop()

    # Open Video Capture
    cap = None
    if isinstance(cap_src, int) and cap_src == 0 and use_dshow:
        cap = cv2.VideoCapture(cap_src, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(cap_src)
    
    # Fallback if capture fails (e.g. webcam not found on cloud server)
    if not cap or not cap.isOpened():
        if cap_src != sample_video and sample_video:
            st.info("ℹ️ Local OpenCV webcam not accessible on cloud server. Select 'Laptop Camera (Browser)' in sidebar or use sample video.")
            cap = cv2.VideoCapture(sample_video)
        
    if not cap or not cap.isOpened():
        st.error("🚨 Unable to access video stream.")
        st.session_state.running = False
        st.stop()

    local_run_id = st.session_state.current_run_id
    prev_time = time.time()
    total_frames = st.session_state.total_frames_scanned
    total_violations = len(st.session_state.session_rows)
    
    fps_history = deque(maxlen=60)
    time_history = deque(maxlen=60)
    
    for f in st.session_state.fps_history:
        fps_history.append(f)
    for t in st.session_state.time_history:
        time_history.append(t)

    try:
        while cap.isOpened() and st.session_state.running:
            # Thread leakage safety check
            if local_run_id != st.session_state.current_run_id:
                break

            ret, frame = cap.read()
            if not ret: 
                break

            total_frames += 1
            st.session_state.total_frames_scanned = total_frames
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect (passing our custom line width and alert classes)
            annotated, detections = detector.detect(rgb, line_width=line_thickness, alert_classes=alert_classes)
            
            # Centroid tracking & deduplication
            rects = [d["bbox"] for d in detections]
            class_names = [d["class_name"] for d in detections]
            
            if "tracker" not in st.session_state or st.session_state.tracker is None:
                st.session_state.tracker = CentroidTracker()
            tracker = st.session_state.tracker
            
            assigned_ids = tracker.update(rects, class_names)
            
            frame_violations = 0
            rows_to_save = []
            
            for idx, d in enumerate(detections):
                class_name = d["class_name"]
                if class_name in alert_classes:
                    frame_violations += 1
                    w_id = assigned_ids[idx] if idx < len(assigned_ids) else "Unknown"
                    
                    # Cooldown deduplication per worker/violation class (15 sec interval)
                    now_ts = time.time()
                    log_key = (w_id, class_name)
                    if log_key not in tracker.logged_violations or (now_ts - tracker.logged_violations[log_key]) > 15.0:
                        tracker.logged_violations[log_key] = now_ts
                        
                        ts_raw = datetime.now()
                        ts = ts_raw.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Save Snap relative to project root snapshots directory
                        snap_id = f"snap_{ts_raw.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                        snap_path = os.path.join("snapshots", snap_id)
                        abs_snap_path = os.path.join(SNAP_DIR, snap_id)
                        cv2.imwrite(abs_snap_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
                        
                        row = [ts, w_id, class_name, d["confidence"], 
                               int(d["bbox"][0]), int(d["bbox"][1]), int(d["bbox"][2]), int(d["bbox"][3]), 
                               snap_path, "Violation"]
                        rows_to_save.append(row)
                        st.session_state.session_rows.append(row)

            if rows_to_save:
                with open(LOG_CSV, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(rows_to_save)
                total_violations += len(rows_to_save)

            # Performance Timing
            now = time.time()
            fps = 1.0 / max(1e-6, (now - prev_time))
            prev_time = now
            fps_history.append(fps)
            time_history.append(datetime.now().strftime("%H:%M:%S"))
            
            st.session_state.fps_history = list(fps_history)
            st.session_state.time_history = list(time_history)

            # Update KPI banner widgets dynamically
            draw_current_kpis(scanned=total_frames, breaches=total_violations, latency=f"{fps:.1f} FPS")

            # Draw the video frame to Streamlit
            video_ph.image(annotated, use_container_width=True)
            
            # Periodic UI updates to reduce streamlit render overhead (every 3 frames)
            if total_frames % 3 == 0:
                # Plotly Chart Update
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(time_history), y=list(fps_history),
                    mode='lines', name='FPS', 
                    line=dict(color='#58a6ff', width=2),
                    fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.08)'
                ))
                fig.update_layout(
                    height=180, margin=dict(l=10, r=10, t=10, b=10),
                    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, visible=False),
                    yaxis=dict(showgrid=False, title=dict(text="FPS", font=dict(color="#58a6ff")), tickfont=dict(color="#58a6ff"))
                )
                metrics_chart_ph.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"fps_chart_{total_frames}")

                # Feed Update (Incident list)
                with feed_ph:
                    if st.session_state.session_rows:
                        recent_logs = st.session_state.session_rows[-4:]
                        for r_log in reversed(recent_logs):
                            draw_incident_card(
                                timestamp=r_log[0].split(" ")[1], 
                                breach_type=r_log[2], 
                                worker_id=r_log[1], 
                                confidence=r_log[3], 
                                snap_path=r_log[8],
                                status=r_log[9]
                            )
                    else:
                        st.info("No safety breaches recorded in this session.")

                # Table Logs Update
                if st.session_state.session_rows:
                    logs_df = pd.DataFrame(st.session_state.session_rows, columns=CSV_HEADER).tail(30)
                    logs_ph.dataframe(logs_df[["timestamp", "worker_id", "violation_type", "confidence", "status"]], use_container_width=True)

            time.sleep(0.005)

    finally:
        cap.release()
        st.session_state.running = False
        st.rerun()

else:
    # Standby / Stopped scan presentation
    if st.session_state.get("session_rows"):
        # Draw completion banner in video feed
        video_ph.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(15,20,35,0.95) 100%);
            border: 1px solid rgba(16,185,129,0.2);
            border-radius: 16px;
            padding: 60px 20px;
            text-align: center;
            box-shadow: inset 0 0 60px rgba(16,185,129,0.03);
        ">
            <div style="font-size:3.5rem; margin-bottom:18px; filter:drop-shadow(0 0 20px rgba(16,185,129,0.4));">🛡️</div>
            <div style="font-size:1.1rem; font-weight:800; color:#ffffff; letter-spacing:0.5px; margin-bottom:10px;">SCAN COMPLETED CLEANLY</div>
            <div style="width:40px; height:2px; background:linear-gradient(90deg,#10b981,#34d399); margin:0 auto 14px;"></div>
            <p style="color:rgba(255,255,255,0.45); font-size:0.82rem; max-width:380px; margin:0 auto; line-height:1.6;">
                The scan session has finished. A total of <b style="color:#10b981;">{len(st.session_state.session_rows)} unique breaches</b> were logged across <b style="color:#3b82f6;">{st.session_state.total_frames_scanned} scanned frames</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Draw the final KPIs
        draw_current_kpis()
        
        # Draw the final Plotly performance chart from session state history
        fig = go.Figure()
        fps_hist = st.session_state.get("fps_history", [])
        time_hist = st.session_state.get("time_history", [])
        if fps_hist:
            fig.add_trace(go.Scatter(
                x=list(time_hist), y=list(fps_hist),
                mode='lines', name='FPS', 
                line=dict(color='#58a6ff', width=2),
                fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.08)'
            ))
        fig.update_layout(
            height=180, margin=dict(l=10, r=10, t=10, b=10),
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, title=dict(text="FPS", font=dict(color="#58a6ff")), tickfont=dict(color="#58a6ff"))
        )
        metrics_chart_ph.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="completed_metrics_chart")
        
        # Draw final incident list
        with feed_ph:
            recent_logs = st.session_state.session_rows[-4:]
            for r_log in reversed(recent_logs):
                draw_incident_card(
                    timestamp=r_log[0].split(" ")[1], 
                    breach_type=r_log[2], 
                    worker_id=r_log[1], 
                    confidence=r_log[3], 
                    snap_path=r_log[8],
                    status=r_log[9]
                )
                
        # Draw the complete audit logs table
        logs_df = pd.DataFrame(st.session_state.session_rows, columns=CSV_HEADER)
        logs_ph.dataframe(logs_df[["timestamp", "worker_id", "violation_type", "confidence", "status"]], use_container_width=True)

    else:
        # Initial Standby Mode
        draw_empty_kpis()
        
        video_ph.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
            border: 1px dashed rgba(96,165,250,0.2);
            border-radius: 16px;
            padding: 80px 20px;
            text-align: center;
            box-shadow: inset 0 0 60px rgba(59,130,246,0.03);
        ">
            <div style="font-size:3.5rem; margin-bottom:18px; filter:drop-shadow(0 0 20px rgba(59,130,246,0.4));">📹</div>
            <div style="font-size:1.1rem; font-weight:800; color:#ffffff; letter-spacing:0.5px; margin-bottom:10px;">CAMERA STREAM STANDBY</div>
            <div style="width:40px; height:2px; background:linear-gradient(90deg,#3b82f6,#8b5cf6); margin:0 auto 14px;"></div>
            <p style="color:rgba(255,255,255,0.35); font-size:0.82rem; max-width:380px; margin:0 auto; line-height:1.6;">
                Select an input source from the sidebar and click <b style="color:#60a5fa;">▶ START SCAN</b> to begin real-time safety monitoring.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        draw_empty_metrics()
