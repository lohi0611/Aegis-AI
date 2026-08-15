"""
AEGIS Safety Intelligence — Main Application
Construction-site PPE compliance monitoring with real-time detection
and persistent SQLite/PostgreSQL violation database.
"""
import os
import time
import csv
import base64
import tempfile
from collections import deque
from datetime import datetime

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ── App modules ───────────────────────────────────────────────────────────────
from ui_utils import (
    apply_custom_css, render_brand_header, kpi_card,
    draw_violation_feed_card, draw_site_status,
    navigation_tip, standby_placeholder, scan_complete_placeholder,
    mission_control_header,
)
from detect import PPEDetector
from db import (
    DB_AVAILABLE, create_scan_session, close_scan_session,
    log_violation_db, get_session_violations,
)
import streamlit.components.v1 as components

# ── Severity helper ───────────────────────────────────────────────────────────
CRITICAL_CLASSES = {"NO-Hardhat", "NO-Safety Vest"}

def severity_for(cls_name: str) -> str:
    return "CRITICAL" if cls_name in CRITICAL_CLASSES else "HIGH"


# ─────────────────────────────────────────────────────────────────────────────
#  CENTROID TRACKER  (deduplication + stable worker IDs)
# ─────────────────────────────────────────────────────────────────────────────
class CentroidTracker:
    def __init__(self, max_disappeared: int = 15, min_distance: int = 100):
        self.next_id          = 101
        self.objects          = {}   # w_id -> (cx, cy)
        self.disappeared      = {}   # w_id -> frames_since_last_seen
        self.classes          = {}   # w_id -> class_name
        self.logged_violations = {}  # (w_id, class_name) -> last_logged_timestamp

        self.max_disappeared = max_disappeared
        self.min_distance    = min_distance

    def register(self, centroid, class_name):
        w_id = f"WKR_{self.next_id}"
        self.objects[w_id]     = centroid
        self.disappeared[w_id] = 0
        self.classes[w_id]     = class_name
        self.next_id += 1
        return w_id

    def deregister(self, w_id):
        for d in (self.objects, self.disappeared, self.classes):
            d.pop(w_id, None)

    def update(self, rects, class_names):
        if len(rects) == 0:
            for w_id in list(self.disappeared):
                self.disappeared[w_id] += 1
                if self.disappeared[w_id] > self.max_disappeared:
                    self.deregister(w_id)
            return []

        input_centroids = [((x1 + x2) // 2, (y1 + y2) // 2)
                           for (x1, y1, x2, y2) in rects]

        if not self.objects:
            return [self.register(c, cn)
                    for c, cn in zip(input_centroids, class_names)]

        obj_ids       = list(self.objects.keys())
        obj_centroids = list(self.objects.values())
        assigned_ids  = [None] * len(input_centroids)
        used_objs     = set()

        for i, (icx, icy) in enumerate(input_centroids):
            best_dist, best_id = float('inf'), None
            for j, w_id in enumerate(obj_ids):
                if w_id in used_objs or self.classes[w_id] != class_names[i]:
                    continue
                ocx, ocy = obj_centroids[j]
                dist = ((icx - ocx) ** 2 + (icy - ocy) ** 2) ** 0.5
                if dist < best_dist and dist < self.min_distance:
                    best_dist, best_id = dist, w_id
            if best_id:
                self.objects[best_id]     = (icx, icy)
                self.disappeared[best_id] = 0
                assigned_ids[i]           = best_id
                used_objs.add(best_id)
            else:
                assigned_ids[i] = self.register((icx, icy), class_names[i])

        for w_id in obj_ids:
            if w_id not in used_objs:
                self.disappeared[w_id] += 1
                if self.disappeared[w_id] > self.max_disappeared:
                    self.deregister(w_id)

        return assigned_ids


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AEGIS | Construction Safety Intelligence",
    page_icon="⛑️",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()

# ── Path resolution ───────────────────────────────────────────────────────────
current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

def resolve_log_csv():
    for c in [
        os.path.join(project_root, "violations.csv"),
        os.path.join(current_dir,  "violations.csv"),
        "violations.csv",
    ]:
        if os.path.exists(c):
            return c
    return os.path.join(project_root, "violations.csv")

LOG_CSV  = resolve_log_csv()
SNAP_DIR = os.path.join(project_root, "snapshots")
os.makedirs(SNAP_DIR, exist_ok=True)

component_dir = os.path.join(current_dir, "camera_component")
auto_camera   = components.declare_component("auto_camera", path=component_dir)

sample_video_paths = [
    os.path.join(current_dir,   "uploaded_video.mp4"),
    os.path.join(project_root,  "uploaded_video.mp4"),
    os.path.join(project_root,  "assets",   "finalTest.mp4"),
    os.path.join(project_root,  "infosys",  "dataset", "source_files", "source_files", "hardhat.mp4"),
    os.path.join(project_root,  "infosys",  "dataset", "source_files", "source_files", "JapanPPE.mp4"),
]
sample_video = next((p for p in sample_video_paths if os.path.exists(p)), None)

VIOLATION_CLASSES = ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
ALL_CLASSES = ["Hardhat", "Mask", "NO-Hardhat", "NO-Mask", "NO-Safety Vest",
               "Person", "Safety Cone", "Safety Vest", "Machinery", "Vehicle"]
CSV_HEADER = ["timestamp", "worker_id", "violation_type", "confidence",
              "x1", "y1", "x2", "y2", "snapshot_path", "status"]

if not os.path.isfile(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        csv.writer(f).writerow(CSV_HEADER)


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
_defaults = {
    "running":             False,
    "session_rows":        [],
    "total_frames_scanned":0,
    "fps_history":         [],
    "time_history":        [],
    "current_run_id":      0,
    "db_session_id":       None,
    "scan_start_time":     None,
    "tracker":             None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 12px;">
        <div style="font-size:2.8rem;filter:drop-shadow(0 0 14px rgba(249,115,22,0.5));">⛑️</div>
        <div style="font-size:1.05rem;font-weight:800;color:#ffffff;letter-spacing:2px;margin-top:6px;">AEGIS AI</div>
        <div style="font-size:0.6rem;color:rgba(241,245,249,0.3);text-transform:uppercase;
            letter-spacing:2.5px;margin-top:3px;">Safety Intelligence Platform</div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(249,115,22,0.2),transparent);
        margin:4px 0 16px;"></div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ CONFIGURATION")

    sources = ["Laptop Camera (Browser)"]
    if sample_video:
        sources.append("Sample Video")
    sources += ["Upload Video File", "Local Webcam (OpenCV)"]
    video_source = st.selectbox("Video Input Source", sources)

    confidence_slider = st.slider("Detection Confidence", 0.1, 1.0, 0.25, step=0.01)
    line_thickness    = st.slider("Bounding Box Thickness", 1, 5, 2)

    alert_classes = st.multiselect(
        "Violations To Monitor",
        options=VIOLATION_CLASSES,
        default=VIOLATION_CLASSES,
    )

    uploaded_file = None
    if video_source == "Upload Video File":
        uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov"])

    use_dshow = st.checkbox("Enhanced Hardware Access (Windows)", value=True)

    st.markdown("---")
    st.markdown("### 🎮 CONTROL PANEL")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        start_btn = st.button("▶ START SCAN")
    with col_c2:
        st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
        stop_btn = st.button("⏹ STOP SCAN")
        st.markdown('</div>', unsafe_allow_html=True)

    if start_btn:
        # Create DB session
        source_map = {
            "Laptop Camera (Browser)": "laptop_camera",
            "Sample Video":            "sample_video",
            "Upload Video File":       "uploaded_video",
            "Local Webcam (OpenCV)":   "local_webcam",
        }
        scan_type   = source_map.get(video_source, "unknown")
        source_name = (uploaded_file.name if uploaded_file
                       else ("browser_camera" if video_source == "Laptop Camera (Browser)"
                             else (os.path.basename(sample_video) if sample_video else "unknown")))

        db_sid = create_scan_session(scan_type, source_name)

        st.session_state.running              = True
        st.session_state.session_rows         = []
        st.session_state.total_frames_scanned = 0
        st.session_state.fps_history          = []
        st.session_state.time_history         = []
        st.session_state.current_run_id      += 1
        st.session_state.db_session_id        = db_sid
        st.session_state.scan_start_time      = time.time()
        st.session_state.tracker              = CentroidTracker()

    if stop_btn:
        st.session_state.running = False
        # Close DB session
        if st.session_state.db_session_id is not None:
            elapsed = time.time() - (st.session_state.scan_start_time or time.time())
            close_scan_session(
                st.session_state.db_session_id,
                total_frames=st.session_state.total_frames_scanned,
                total_violations=len(st.session_state.session_rows),
                status="stopped",
            )

    navigation_tip()

    if DB_AVAILABLE:
        st.markdown('<div class="db-status-ok" style="margin-top:8px;">⬤ Database connected</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="db-status-off" style="margin-top:8px;">⬤ DB offline — CSV fallback active</div>',
                    unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  BRAND HEADER
# ─────────────────────────────────────────────────────────────────────────────
render_brand_header(
    is_scanning=st.session_state.running,
    db_ok=DB_AVAILABLE,
)


# ─────────────────────────────────────────────────────────────────────────────
#  KPI BANNER
# ─────────────────────────────────────────────────────────────────────────────
ORANGE = "#f97316"; RED = "#ef4444"; GREEN = "#22c55e"; TEAL = "#06b6d4"; AMBER = "#fbbf24"

def compute_kpis():
    rows      = st.session_state.session_rows
    breaches  = len(rows)
    critical  = sum(1 for r in rows if severity_for(r[2]) == "CRITICAL")
    frames    = st.session_state.total_frames_scanned
    fps_hist  = st.session_state.fps_history
    avg_fps   = (sum(fps_hist) / len(fps_hist)) if fps_hist else 0
    score     = max(0, round((1 - breaches / max(frames, 1)) * 100, 1)) if frames > 0 else 100.0
    elapsed   = time.time() - (st.session_state.scan_start_time or time.time())
    dur_str   = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}" if st.session_state.scan_start_time else "00:00"
    return breaches, critical, frames, avg_fps, score, dur_str

kpi_cols = st.columns(6)
kpi_ph   = [c.empty() for c in kpi_cols]    # placeholders, updated during scan

def render_kpis(breaches, critical, frames, avg_fps, score, dur_str):
    with kpi_cols[0]: kpi_card("Violations", str(breaches), "🚨", RED)
    with kpi_cols[1]: kpi_card("Critical", str(critical), "🔥", RED if critical else GREEN)
    with kpi_cols[2]: kpi_card("Frames Scanned", str(frames), "👁️", TEAL)
    with kpi_cols[3]: kpi_card("Safety Score", f"{score}%", "🛡️",
                                GREEN if score >= 80 else AMBER if score >= 50 else RED)
    with kpi_cols[4]: kpi_card("Sensor FPS", f"{avg_fps:.1f}" if avg_fps else "STANDBY", "⚡", TEAL)
    with kpi_cols[5]: kpi_card("Scan Duration", dur_str, "⏱️", ORANGE)

render_kpis(0, 0, 0, 0, 100.0, "00:00")
st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN MONITORING GRID
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2.5, 1.2])

with col_left:
    st.markdown('<div class="section-title">📹 Live Safety Monitor</div>', unsafe_allow_html=True)
    video_ph = st.empty()

with col_right:
    st.markdown('<div class="section-title">⚠️ Site Status</div>', unsafe_allow_html=True)
    status_ph = st.empty()
    st.markdown('<div class="section-title" style="margin-top:12px;">🚨 Live Violation Feed</div>',
                unsafe_allow_html=True)
    feed_ph = st.container()

# ── Lower section ─────────────────────────────────────────────────────────────
st.markdown("---")
c_perf, c_logs = st.columns([1.5, 2.2])

with c_perf:
    st.markdown('<div class="section-title">📈 Scan Performance</div>', unsafe_allow_html=True)
    perf_ph = st.empty()

with c_logs:
    st.markdown('<div class="section-title">📋 Violation Log</div>', unsafe_allow_html=True)
    logs_ph = st.empty()


# ─────────────────────────────────────────────────────────────────────────────
#  SHARED VIOLATION LOGGING HELPER
# ─────────────────────────────────────────────────────────────────────────────
def log_violation(tracker, w_id, d, frame_number, annotated_frame):
    """
    Check cooldown → log to session_state, CSV, and DB.
    Returns the row dict if a new violation was logged, else None.
    """
    cls_name = d["class_name"]
    now_ts   = time.time()
    log_key  = (w_id, cls_name)
    COOLDOWN = 15.0  # seconds

    if (log_key in tracker.logged_violations and
            (now_ts - tracker.logged_violations[log_key]) < COOLDOWN):
        return None  # still within cooldown — deduplicated

    tracker.logged_violations[log_key] = now_ts

    ts_raw  = datetime.now()
    ts_str  = ts_raw.strftime("%Y-%m-%d %H:%M:%S")
    bbox    = [int(d["bbox"][0]), int(d["bbox"][1]),
               int(d["bbox"][2]), int(d["bbox"][3])]

    # Snapshot
    snap_id  = f"snap_{ts_raw.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    snap_rel = os.path.join("snapshots", snap_id)
    snap_abs = os.path.join(SNAP_DIR, snap_id)
    try:
        cv2.imwrite(snap_abs, cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))
    except Exception:
        snap_rel = ""

    row = [ts_str, w_id, cls_name, d["confidence"],
           bbox[0], bbox[1], bbox[2], bbox[3], snap_rel, "Violation"]
    st.session_state.session_rows.append(row)

    # CSV
    try:
        with open(LOG_CSV, "a", newline="") as f:
            csv.writer(f).writerow(row)
    except Exception:
        pass

    # Database
    log_violation_db(
        session_id=st.session_state.db_session_id,
        worker_id=w_id,
        violation_type=cls_name,
        timestamp=ts_raw,
        frame_number=frame_number,
        confidence=d["confidence"],
        bbox=bbox,
        snapshot_path=snap_rel,
    )

    return row


# ─────────────────────────────────────────────────────────────────────────────
#  SHARED UI REFRESH
# ─────────────────────────────────────────────────────────────────────────────
def refresh_ui(annotated, fps, total_frames, fps_history, time_history):
    """Refresh video, KPIs, perf chart, feed and log table."""
    video_ph.image(annotated, use_container_width=True)

    breaches, critical, frames, avg_fps, score, dur_str = compute_kpis()
    render_kpis(breaches, critical, total_frames, fps, score, dur_str)

    # Site status panel
    with status_ph:
        draw_site_status(breaches, critical)

    # Performance chart
    fig = go.Figure()
    if fps_history:
        fig.add_trace(go.Scatter(
            x=list(time_history), y=list(fps_history),
            mode="lines",
            line=dict(color="#f97316", width=2),
            fill="tozeroy",
            fillcolor="rgba(249,115,22,0.08)",
        ))
    fig.update_layout(
        height=170, margin=dict(l=10, r=10, t=10, b=10),
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, title=dict(text="FPS", font=dict(color="#f97316")),
                   tickfont=dict(color="#f97316")),
    )
    perf_ph.plotly_chart(fig, use_container_width=True,
                         config={"displayModeBar": False},
                         key=f"fps_chart_{total_frames}")

    # Violation feed
    with feed_ph:
        if st.session_state.session_rows:
            recent = st.session_state.session_rows[-5:]
            for r in reversed(recent):
                draw_violation_feed_card(
                    timestamp=r[0].split(" ")[1],
                    violation_type=r[2],
                    worker_id=r[1],
                    confidence=float(r[3]),
                    severity=severity_for(r[2]),
                    status=r[9],
                )
        else:
            st.info("No violations detected yet.")

    # Violation log table
    if st.session_state.session_rows:
        df = pd.DataFrame(st.session_state.session_rows, columns=CSV_HEADER).tail(40)
        df["severity"] = df["violation_type"].apply(severity_for)
        logs_ph.dataframe(
            df[["timestamp", "worker_id", "violation_type", "severity", "confidence", "status"]],
            use_container_width=True,
        )


def draw_empty_perf():
    fig = go.Figure()
    fig.update_layout(
        height=170, margin=dict(l=10, r=10, t=10, b=10),
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False),
    )
    perf_ph.plotly_chart(fig, use_container_width=True,
                         config={"displayModeBar": False}, key="empty_perf_chart")
    logs_ph.info("Awaiting scan activation…")


# ─────────────────────────────────────────────────────────────────────────────
#  DETECTION ENGINE — LAPTOP CAMERA (BROWSER)
# ─────────────────────────────────────────────────────────────────────────────
if video_source == "Laptop Camera (Browser)":
    if st.session_state.running:
        detector = PPEDetector(conf=confidence_slider)
        val = auto_camera(key="auto_camera_key")

        if not val:
            video_ph.info("📷 Connecting to camera… Please allow browser camera access.")
        elif isinstance(val, str) and val.startswith("ERROR:"):
            st.error(f"Webcam Error: {val}")
            st.session_state.running = False
            st.rerun()
        elif isinstance(val, str) and val.startswith("data:image/jpeg;base64,"):
            _, encoded = val.split(",", 1)
            nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            st.session_state.total_frames_scanned += 1
            annotated, detections = detector.detect(frame, line_width=line_thickness,
                                                    alert_classes=alert_classes)

            rects       = [d["bbox"] for d in detections]
            class_names = [d["class_name"] for d in detections]

            if not st.session_state.tracker:
                st.session_state.tracker = CentroidTracker()
            tracker      = st.session_state.tracker
            assigned_ids = tracker.update(rects, class_names)

            for idx, d in enumerate(detections):
                if d["class_name"] in alert_classes:
                    w_id = assigned_ids[idx] if idx < len(assigned_ids) else "Unknown"
                    log_violation(tracker, w_id, d,
                                  st.session_state.total_frames_scanned, annotated)

            # FPS
            now = time.time()
            if "prev_time" not in st.session_state:
                st.session_state.prev_time = now
            fps = 1.0 / max(1e-6, now - st.session_state.prev_time)
            st.session_state.prev_time = now
            st.session_state.fps_history.append(fps)
            st.session_state.time_history.append(datetime.now().strftime("%H:%M:%S"))
            if len(st.session_state.fps_history) > 60:
                st.session_state.fps_history.pop(0)
                st.session_state.time_history.pop(0)

            refresh_ui(annotated, fps, st.session_state.total_frames_scanned,
                       st.session_state.fps_history, st.session_state.time_history)
    else:
        # Standby / post-scan state handled below in else block
        pass


# ─────────────────────────────────────────────────────────────────────────────
#  DETECTION ENGINE — VIDEO / LOCAL WEBCAM
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.running:
    detector = PPEDetector(conf=confidence_slider)

    # Resolve capture source
    cap_src = None
    if video_source == "Sample Video" and sample_video:
        cap_src = sample_video
    elif video_source == "Upload Video File":
        if uploaded_file:
            tmp = tempfile.NamedTemporaryFile(
                delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
            tmp.write(uploaded_file.read())
            tmp.close()
            cap_src = tmp.name
        else:
            st.warning("⚠️ Please upload a video file to begin.")
            st.session_state.running = False
            st.stop()
    elif video_source == "Local Webcam (OpenCV)":
        cap_src = 0

    if cap_src is None:
        if sample_video:
            cap_src = sample_video
            st.info("ℹ️ Using sample video for demonstration.")
        else:
            st.warning("⚠️ Please upload a video file or select a valid source.")
            st.session_state.running = False
            st.stop()

    # Open capture
    if isinstance(cap_src, int) and use_dshow:
        cap = cv2.VideoCapture(cap_src, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(cap_src)

    if not cap.isOpened() and cap_src != sample_video and sample_video:
        st.info("ℹ️ Local webcam not available on cloud. Falling back to sample video.")
        cap = cv2.VideoCapture(sample_video)

    if not cap.isOpened():
        st.error("🚨 Unable to open video stream.")
        st.session_state.running = False
        st.stop()

    local_run_id = st.session_state.current_run_id
    prev_time    = time.time()
    total_frames = st.session_state.total_frames_scanned
    fps_history  = deque(list(st.session_state.fps_history),  maxlen=60)
    time_history = deque(list(st.session_state.time_history), maxlen=60)

    if not st.session_state.tracker:
        st.session_state.tracker = CentroidTracker()
    tracker = st.session_state.tracker

    try:
        while cap.isOpened() and st.session_state.running:
            if local_run_id != st.session_state.current_run_id:
                break

            ret, frame = cap.read()
            if not ret:
                break

            total_frames += 1
            st.session_state.total_frames_scanned = total_frames

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            annotated, detections = detector.detect(rgb, line_width=line_thickness,
                                                    alert_classes=alert_classes)

            rects       = [d["bbox"] for d in detections]
            class_names = [d["class_name"] for d in detections]
            assigned_ids = tracker.update(rects, class_names)

            for idx, d in enumerate(detections):
                if d["class_name"] in alert_classes:
                    w_id = assigned_ids[idx] if idx < len(assigned_ids) else "Unknown"
                    log_violation(tracker, w_id, d, total_frames, annotated)

            # FPS
            now = time.time()
            fps = 1.0 / max(1e-6, now - prev_time)
            prev_time = now
            fps_history.append(fps)
            time_history.append(datetime.now().strftime("%H:%M:%S"))
            st.session_state.fps_history  = list(fps_history)
            st.session_state.time_history = list(time_history)

            # Render every 3 frames to reduce overhead
            if total_frames % 3 == 0 or total_frames == 1:
                refresh_ui(annotated, fps, total_frames, fps_history, time_history)

            time.sleep(0.005)

    finally:
        cap.release()
        # Mark DB session complete
        if st.session_state.db_session_id is not None:
            close_scan_session(
                st.session_state.db_session_id,
                total_frames=st.session_state.total_frames_scanned,
                total_violations=len(st.session_state.session_rows),
                status="completed",
            )
        st.session_state.running = False
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  STANDBY / POST-SCAN STATE
# ─────────────────────────────────────────────────────────────────────────────
else:
    if st.session_state.session_rows:
        # Post-scan summary
        rows     = st.session_state.session_rows
        frames   = st.session_state.total_frames_scanned
        breaches = len(rows)
        critical = sum(1 for r in rows if severity_for(r[2]) == "CRITICAL")

        elapsed = 0.0
        if st.session_state.scan_start_time:
            elapsed = time.time() - st.session_state.scan_start_time
        dur_str = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"

        with video_ph:
            scan_complete_placeholder(breaches, frames, dur_str)

        render_kpis(breaches, critical, frames,
                    (sum(st.session_state.fps_history) / len(st.session_state.fps_history)
                     if st.session_state.fps_history else 0),
                    max(0, round((1 - breaches / max(frames, 1)) * 100, 1)),
                    dur_str)

        with status_ph:
            draw_site_status(breaches, critical)

        # Perf chart from history
        fig = go.Figure()
        if st.session_state.fps_history:
            fig.add_trace(go.Scatter(
                x=list(st.session_state.time_history),
                y=list(st.session_state.fps_history),
                mode="lines",
                line=dict(color="#f97316", width=2),
                fill="tozeroy",
                fillcolor="rgba(249,115,22,0.08)",
            ))
        fig.update_layout(
            height=170, margin=dict(l=10, r=10, t=10, b=10),
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, title=dict(text="FPS", font=dict(color="#f97316")),
                       tickfont=dict(color="#f97316")),
        )
        perf_ph.plotly_chart(fig, use_container_width=True,
                             config={"displayModeBar": False}, key="post_scan_perf")

        with feed_ph:
            recent = rows[-5:]
            for r in reversed(recent):
                draw_violation_feed_card(
                    timestamp=r[0].split(" ")[1],
                    violation_type=r[2],
                    worker_id=r[1],
                    confidence=float(r[3]),
                    severity=severity_for(r[2]),
                    status=r[9],
                )

        df = pd.DataFrame(rows, columns=CSV_HEADER)
        df["severity"] = df["violation_type"].apply(severity_for)
        logs_ph.dataframe(
            df[["timestamp", "worker_id", "violation_type", "severity", "confidence", "status"]],
            use_container_width=True,
        )

        # Download button
        st.download_button(
            "⬇️ Download Violation Report (CSV)",
            data=df.to_csv(index=False),
            file_name=f"aegis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    else:
        # Initial standby
        render_kpis(0, 0, 0, 0, 100.0, "00:00")
        with video_ph:
            standby_placeholder()
        with status_ph:
            draw_site_status(0, 0)
        draw_empty_perf()
