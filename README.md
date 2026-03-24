# 🛡️ Aegis: AI-Powered Workplace Compliance Monitor

**SafetyEye** is a state-of-the-art computer vision system designed to automate safety audits in industrial and construction environments. Using high-speed object detection, the system ensures that every person on-site is protected by the required Personal Protective Equipment (PPE).

---

### 🚀 Key Features
*   **Real-time PPE Detection**: Instantly identifies Hardhats, Safety Vests, and Masks using a custom-trained **YOLOv8** model.
*   **Automatic Violation Logging**: Captures snapshots and logs the moment a safety protocol is breached.
*   **Tactical Command Dashboard**: A premium **Streamlit** interface featuring live optic arrays, performance metrics (FPS), and behavioral analytics.
*   **Flexible Inputs**: Supports live Webcam feeds and video file uploads for historical auditing.
*   **Remote Monitoring**: Integration support for Localtunnel to share the safety feed globally.

---

### 💻 Installation & Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/YourUsername/Safety-Monitor.git
    cd Safety-Monitor
    ```

2.  **Initialize Virtual Environment**:
    ```bash
    python -m venv .venv
    ```

3.  **Install Requirements**:
    ```bash
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    ```

---

### ⚡ How to Run

#### **Option 1: The Easy Way (Windows)**
Simply **Double-Click** the `run_app.bat` file in the project folder. This will automatically:
*   Activate the virtual environment.
*   Launch the AI Dashboard in your browser.

#### **Option 2: Terminal**
```bash
streamlit run dashboard/app.py
```

---

### 🛠️ Tech Stack
*   **AI Engine**: YOLOv8 (Ultralytics)
*   **Interface**: Streamlit (Premium UI Design)
*   **Data Science**: Pandas, Plotly, OpenCV
*   **Runtime**: Python 3.12 (inside .venv)

---

### 📈 Project Gallery
*   **Model Weights**: Located in `/models/yolov8_ppe.pt`
*   **Violation Logs**: Recorded automatically in `violations.csv`
*   **Event Snapshots**: Saved to the `/snapshots` directory
