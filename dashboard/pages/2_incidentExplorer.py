import os
import time
import pandas as pd
import streamlit as st
from datetime import datetime

# Import UI Utils
from ui_utils import apply_custom_css, mission_control_header, kpi_card

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="AegisAI | Incident Explorer",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling
apply_custom_css()

# ===================== ABSOLUTE PATH RESOLUTION =====================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
LOG_CSV = os.path.join(project_root, "violations.csv")

# Resolve image paths dynamically
def get_image_path(stored_path):
    if not stored_path or pd.isna(stored_path):
        return None
    stored_path = str(stored_path).replace("\\", "/")
    filename = os.path.basename(stored_path)
    
    check_paths = [
        os.path.join(project_root, stored_path),
        os.path.join(project_root, "dashboard", stored_path),
        os.path.join(project_root, "snapshots", filename),
        os.path.join(project_root, "dashboard", "snapshots", filename),
        os.path.join(current_dir, "snapshots", filename),
        os.path.join(current_dir, filename)
    ]
    for p in check_paths:
        if os.path.exists(p):
            return p
    return None

# Load CSV safely
def load_data():
    if not os.path.exists(LOG_CSV):
        return pd.DataFrame()
    try:
        df = pd.read_csv(LOG_CSV)
        if df.empty:
            return df
        if "status" not in df.columns:
            df["status"] = "Violation"
        else:
            df["status"] = df["status"].fillna("Violation")
        return df
    except Exception as e:
        st.error(f"Error loading logs: {e}")
        return pd.DataFrame()

df_raw = load_data()

# Update CSV status transactionally
def update_incident_status(row_idx, new_status):
    try:
        # Load fresh copy to prevent race conditions
        df_update = pd.read_csv(LOG_CSV)
        if "status" not in df_update.columns:
            df_update["status"] = "Violation"
        df_update.at[row_idx, "status"] = new_status
        df_update.to_csv(LOG_CSV, index=False)
        st.toast(f"ℹ️ Incident #{row_idx + 1} status updated to: {new_status}", icon="🛡️")
        time.sleep(0.5)
        st.rerun()
    except Exception as e:
        st.error(f"Error writing to logs database: {e}")

# ===================== SIDEBAR FILTERS =====================
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><span style="font-size: 2.2rem; filter: drop-shadow(0 0 10px rgba(88, 166, 255, 0.35));">🚨</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.3rem; font-weight: 800; color: #ffffff; text-align: center; letter-spacing: 2px; margin-bottom: 5px;">EXPLORER</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); text-align: center; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 25px;">Database Query Console</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔍 SEARCH & QUERY")
    
    # Search input
    search_query = st.text_input("Search Worker ID", "").strip()
    
    # Status filter
    status_filter = st.multiselect(
        "Incident Status",
        options=["Violation", "Resolved", "Dismissed"],
        default=["Violation", "Resolved"]
    )
    
    # Class Filter
    class_filter = st.multiselect(
        "Breach Category",
        options=["NO-Hardhat", "NO-Mask", "NO-Safety Vest"],
        default=["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
    )
    
    # Sort
    sort_by = st.selectbox(
        "Sort Order",
        options=["Newest First", "Oldest First", "Confidence (High -> Low)"]
    )
    
    st.markdown("---")
    st.info("💡 **Tip:** Clicking Resolve/Dismiss on any card will instantly update the safety record in `violations.csv`.")

# ===================== TITLE HEADER =====================
mission_control_header("AEGIS <span style='color:#f85149;'>INCIDENT LOG EXPLORER</span>", 
                      "SECURE SURVEILLANCE SNAPSHOT AUDITS & INTERACTIVE INCIDENT RESOLUTION")

# Empty check
if df_raw.empty:
    st.info("💤 **No incident records detected.** Launch active neural scans in the main Command Center to generate logs.")
    st.stop()

# ===================== APPLY FILTERS =====================
# Remember original row indexes for database updates
df_filtered = df_raw.copy()
df_filtered["original_idx"] = df_filtered.index

# Apply search
if search_query:
    df_filtered = df_filtered[df_filtered["worker_id"].astype(str).str.contains(search_query, case=False)]

# Apply status
if status_filter:
    df_filtered = df_filtered[df_filtered["status"].isin(status_filter)]

# Apply class
if class_filter:
    df_filtered = df_filtered[df_filtered["violation_type"].isin(class_filter)]

# Apply sort
if sort_by == "Newest First":
    df_filtered = df_filtered.sort_values(by="timestamp", ascending=False)
elif sort_by == "Oldest First":
    df_filtered = df_filtered.sort_values(by="timestamp", ascending=True)
elif sort_by == "Confidence (High -> Low)":
    df_filtered = df_filtered.sort_values(by="confidence", ascending=False)

total_filtered = len(df_filtered)

# Show Quick KPI Counts
kcol1, kcol2, kcol3 = st.columns(3)
with kcol1:
    kpi_card("Query Matches", total_filtered, "🎯", "#58a6ff")
with kcol2:
    kpi_card("Active Breaches", len(df_filtered[df_filtered["status"] == "Violation"]), "🚨", "#f85149")
with kcol3:
    kpi_card("Resolved Cases", len(df_filtered[df_filtered["status"] == "Resolved"]), "✅", "#56d364")

st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

# ===================== PAGINATION =====================
ITEMS_PER_PAGE = 6
total_pages = max(1, -(-total_filtered // ITEMS_PER_PAGE)) # ceiling division

# Page selector in main area (clean center style)
pcol1, pcol2, pcol3 = st.columns([2, 1, 2])
with pcol2:
    page = st.number_input("Page selector", min_value=1, max_value=total_pages, value=1, step=1, label_visibility="collapsed")
    st.markdown(f'<p style="text-align:center; font-size:0.8rem; color:rgba(255,255,255,0.4); margin-top:-5px;">Page {page} of {total_pages}</p>', unsafe_allow_html=True)

# Get slice
start_idx = (page - 1) * ITEMS_PER_PAGE
end_idx = start_idx + ITEMS_PER_PAGE
df_page = df_filtered.iloc[start_idx:end_idx]

# ===================== GRID PRESENTATION =====================
if df_page.empty:
    st.info("No safety breaches match your active filters.")
else:
    # 3-column grid
    cols = st.columns(3)
    
    for i, (_, row) in enumerate(df_page.iterrows()):
        col = cols[i % 3]
        orig_idx = int(row["original_idx"])
        
        # Get resolved image path
        img_path = get_image_path(row["snapshot_path"])
        
        # Draw Incident Card inside column
        with col:
            st.markdown(f'<div class="glass-card" style="margin-bottom:15px; border-top: 3px solid {"#f85149" if row["status"] == "Violation" else "#56d364" if row["status"] == "Resolved" else "#e3b341"};">', unsafe_allow_html=True)
            
            # Show Image Snapshot
            if img_path:
                st.image(img_path, use_container_width=True)
            else:
                # Tech-looking warning placeholder
                st.markdown("""
                <div style="background-color:#161f30; height:150px; display:flex; flex-direction:column; align-items:center; justify-content:center; border-radius:8px; margin-bottom:10px;">
                    <span style="font-size:2.5rem; margin-bottom:5px;">📷</span>
                    <span style="font-size:0.75rem; color:rgba(255,255,255,0.35); text-transform:uppercase; letter-spacing:1px;">Snapshot Offline</span>
                </div>
                """, unsafe_allow_html=True)
                
            # Details Layout
            st.markdown(f"""
            <div style="margin-top: 10px; margin-bottom: 12px;">
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:rgba(255,255,255,0.4); font-family: 'JetBrains Mono', monospace; margin-bottom:5px;">
                    <span>IDX: #{orig_idx+1}</span>
                    <span>{row["timestamp"]}</span>
                </div>
                <h4 style="margin: 0 0 6px 0; color:#ffffff; font-weight:700;">{row["violation_type"]}</h4>
                <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:rgba(255,255,255,0.7);">
                    <span>Worker: <b style="color:#58a6ff;">{row["worker_id"]}</b></span>
                    <span>Confidence: <b style="color:#00d4ff; font-family: 'JetBrains Mono';">{row["confidence"]:.2f}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Interactive Action Selectbox
            status_options = ["Violation", "Resolved", "Dismissed"]
            curr_status = row["status"]
            if curr_status not in status_options:
                status_options.append(curr_status)
                
            selected_action = st.selectbox(
                "Change Action Status",
                options=status_options,
                index=status_options.index(curr_status),
                key=f"status_select_{orig_idx}",
                label_visibility="collapsed"
            )
            
            # Write to CSV if changed
            if selected_action != curr_status:
                update_incident_status(orig_idx, selected_action)
                
            st.markdown("</div>", unsafe_allow_html=True)
