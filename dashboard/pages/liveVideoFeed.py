import streamlit as st
import cv2
import time
import numpy as np

# FIXED IMPORT (no dashboard.)
from detect import PPEDetector


def run_live_feed():
    st.set_page_config(page_title="Live Video Nodes", layout="wide")
    st.markdown('<h1 style="color:#1e3a8a;">📹 Live Video Nodes</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar Controls
    with st.sidebar:
        st.header("⚙️ Node Selection")
        video_source = st.selectbox("Select Feed", ["Webcam (0)", "External Cam (1)", "Video File"])
        confidence = st.slider("Neural Threshold", 0.1, 1.0, 0.5)
        run_detection = st.checkbox("Initialize AI Scanner")
        
        st.markdown("---")
        st.info("💡 **Navigation View:** Use the sidebar to return to the monitoring terminal.")

    # Select source logic
    if video_source == "Webcam (0)": source = 0
    elif video_source == "External Cam (1)": source = 1
    else: source = st.file_uploader("Upload Node Feed", type=["mp4", "avi"])

    detector = PPEDetector(conf=confidence)
    frame_placeholder = st.empty()
    fps_placeholder = st.empty()

    if run_detection:
        if video_source == "Video File":
            if source:
                temp_path = "uploaded_video.mp4"
                with open(temp_path, "wb") as f: f.write(source.read())
                cap = cv2.VideoCapture(temp_path)
            else:
                st.warning("Please upload a video file.")
                st.stop()
        else:
            cap = cv2.VideoCapture(source)

        prev_time = time.time()
        while cap.isOpened() and run_detection:
            ret, frame = cap.read()
            if not ret: break
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            annotated, _ = detector.detect(rgb)
            
            curr = time.time()
            fps = 1 / (curr - prev_time)
            prev_time = curr

            frame_placeholder.image(annotated, use_container_width=True)
            fps_placeholder.markdown(f"### ⚡ NODE FPS: `{fps:.2f}`")

        cap.release()

if __name__ == "__main__":
    run_live_feed()
