import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import UI Utils
from ui_utils import apply_custom_css, mission_control_header, kpi_card

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="AegisAI | Compliance Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Styling
apply_custom_css()

# ===================== ABSOLUTE PATH RESOLUTION =====================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
LOG_CSV = os.path.join(project_root, "violations.csv")

# Load CSV safely
def load_data():
    if not os.path.exists(LOG_CSV):
        return pd.DataFrame()
    try:
        df = pd.read_csv(LOG_CSV)
        if df.empty:
            return df
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        # Ensure status column exists, default to 'Violation' if missing
        if "status" not in df.columns:
            df["status"] = "Violation"
        else:
            df["status"] = df["status"].fillna("Violation")
        return df
    except Exception as e:
        st.error(f"Error loading logs: {e}")
        return pd.DataFrame()

df_raw = load_data()

# ===================== SIDEBAR FILTERS =====================
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><span style="font-size: 2.2rem; filter: drop-shadow(0 0 10px rgba(88, 166, 255, 0.35));">📊</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.3rem; font-weight: 800; color: #ffffff; text-align: center; letter-spacing: 2px; margin-bottom: 5px;">ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); text-align: center; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 25px;">Safety Audit Sub-Node</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📅 DATE FILTER")
    
    if not df_raw.empty:
        min_date = df_raw["timestamp"].min().date()
        max_date = df_raw["timestamp"].max().date()
        
        # Date range picker
        date_range = st.date_input(
            "Select Audit Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        st.info("No logs available to filter dates.")
        date_range = None
        
    st.markdown("### 🎛️ FILTERS")
    
    # Violation Type Filter
    all_types = ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
    selected_types = st.multiselect(
        "Violation Category",
        options=all_types,
        default=all_types
    )
    
    st.markdown("---")
    st.info("💡 **Navigation:** Use the sidebar menu to return to **Operations Command** or go to the **Incident Explorer**.")

# ===================== TITLE HEADER =====================
mission_control_header("AEGIS <span style='color:#58a6ff;'>STRATEGIC ANALYTICS</span>", 
                      "OPERATIONAL VIOLATION HEATMAPS & SAFETY PERFORMANCE INTELLIGENCE")

# Check if data is empty
if df_raw.empty:
    st.info("💤 **Awaiting Data Initialization.** Start active scans in the Command Center to populate compliance charts.")
    st.stop()

# ===================== FILTER DATA =====================
df = df_raw.copy()

# Date range filtering
if date_range and len(date_range) == 2:
    start_dt = pd.to_datetime(date_range[0])
    end_dt = pd.to_datetime(date_range[1]) + timedelta(days=1)
    df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] < end_dt)]

# Violation type filtering
if selected_types:
    df = df[df["violation_type"].isin(selected_types)]

# Calculate statistics
total_logs = len(df)
active_violations = len(df[df["status"] == "Violation"])
resolved_incidents = len(df[df["status"] == "Resolved"])
dismissed_incidents = len(df[df["status"] == "Dismissed"])

# Smart compliance score: starts at 96% baseline, drops with active violations, rises with resolved/dismissed ones.
if total_logs == 0:
    compliance_score = 100.0
else:
    compliance_score = max(0.0, 97.5 - (active_violations * 0.12))
    compliance_score = min(100.0, compliance_score + (resolved_incidents * 0.12) + (dismissed_incidents * 0.08))

# High risk hour calculation
if not df.empty:
    df['hour'] = df['timestamp'].dt.hour
    risk_hour_counts = df['hour'].value_counts()
    if not risk_hour_counts.empty:
        high_risk_hour = f"{risk_hour_counts.index[0]:02d}:00"
    else:
        high_risk_hour = "N/A"
else:
    high_risk_hour = "N/A"

# ===================== KPI ROW =====================
col_k1, col_k2, col_k3, col_k4 = st.columns(4)

with col_k1:
    kpi_card("Overall Compliance", f"{compliance_score:.1f}%", "🛡️", "#56d364" if compliance_score > 90 else "#e3b341", alert_type="success" if compliance_score > 90 else None)
with col_k2:
    kpi_card("Unresolved Breaches", active_violations, "🚨", "#f85149", alert_type="danger" if active_violations > 5 else None)
with col_k3:
    kpi_card("Resolved Incidents", resolved_incidents, "✅", "#56d364")
with col_k4:
    kpi_card("Peak Breach Hour", high_risk_hour, "⏰", "#00d4ff")

st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)

# ===================== CHART LAYER 1 =====================
col_c1, col_c2 = st.columns([1.2, 1.8])

with col_c1:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">📊 Compliance Gauge</h3>', unsafe_allow_html=True)
    
    # Custom Dial Gauge Chart using Plotly
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = compliance_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        number = {'suffix': "%", 'font': {'size': 40, 'color': '#ffffff', 'family': 'Outfit'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#888888"},
            'bar': {'color': "#58a6ff"},
            'bgcolor': "rgba(13, 19, 31, 0.6)",
            'borderwidth': 1,
            'bordercolor': "rgba(255,255,255,0.08)",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(248, 81, 73, 0.15)'},
                {'range': [60, 85], 'color': 'rgba(210, 153, 34, 0.15)'},
                {'range': [85, 100], 'color': 'rgba(46, 160, 67, 0.15)'}
            ],
            'threshold': {
                'line': {'color': "#00d4ff", 'width': 3},
                'thickness': 0.75,
                'value': 90.0
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False}, key="gauge_chart")

with col_c2:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">⚠️ Category Breakdown</h3>', unsafe_allow_html=True)
    if not df.empty:
        type_counts = df["violation_type"].value_counts().reset_index()
        type_counts.columns = ["Violation Type", "Count"]
        
        # Donut chart
        fig_donut = px.pie(
            type_counts, 
            names="Violation Type", 
            values="Count", 
            hole=0.45,
            color="Violation Type",
            color_discrete_map={
                "NO-Hardhat": "#f85149",
                "NO-Mask": "#e3b341",
                "NO-Safety Vest": "#58a6ff"
            }
        )
        
        fig_donut.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            marker=dict(line=dict(color='rgba(6,9,15,1)', width=2))
        )
        
        fig_donut.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            template="plotly_dark"
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False}, key="donut_chart")
    else:
        st.info("No data available for breakdown.")

# ===================== CHART LAYER 2 =====================
st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([1.8, 1.2])

with col_h1:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">🔥 Breach Intensity Heatmap</h3>', unsafe_allow_html=True)
    if not df.empty:
        df['hour'] = df['timestamp'].dt.hour
        df['day_name'] = df['timestamp'].dt.day_name()
        
        # Group and pivot
        heatmap_df = df.groupby(['day_name', 'hour']).size().reset_index(name='count')
        
        # Create standard layout
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours_order = list(range(24))
        
        # Build grid
        grid = pd.DataFrame(0, index=days_order, columns=hours_order)
        for _, row in heatmap_df.iterrows():
            if row['day_name'] in days_order:
                grid.at[row['day_name'], row['hour']] = row['count']
                
        # Heatmap figure
        fig_heat = px.imshow(
            grid,
            labels=dict(x="Hour of Day", y="Day of Week", color="Breaches Count"),
            x=[f"{h:02d}:00" for h in hours_order],
            y=days_order,
            color_continuous_scale="Reds",
        )
        
        fig_heat.update_layout(
            height=260,
            margin=dict(l=20, r=20, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            template="plotly_dark",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False}, key="heat_chart")
    else:
        st.info("No data available for heatmap.")

with col_h2:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">👷 Worker Compliance</h3>', unsafe_allow_html=True)
    if not df.empty and "worker_id" in df.columns:
        # Tally active violations per worker
        worker_violations = df[df["status"] == "Violation"]["worker_id"].value_counts().reset_index()
        worker_violations.columns = ["Worker ID", "Active Breaches"]
        
        # Show top 5 workers in a clean bar chart
        top_workers = worker_violations.head(5)
        if not top_workers.empty:
            fig_bar = px.bar(
                top_workers,
                x="Active Breaches",
                y="Worker ID",
                orientation='h',
                color="Active Breaches",
                color_continuous_scale="Reds"
            )
            
            fig_bar.update_layout(
                height=260,
                margin=dict(l=20, r=20, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                template="plotly_dark",
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False}, key="bar_chart")
        else:
            st.success("No active violations logged for any workers!")
    else:
        st.info("No worker-specific logs found.")

# ===================== SUMMARY & DOWNLOADS =====================
st.markdown("---")
col_s1, col_s2 = st.columns([2.2, 1])

with col_s1:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">🧠 Safety Command Advisor</h3>', unsafe_allow_html=True)
    
    # Dynamically generate reports
    if compliance_score > 93:
        st.markdown("""
        <div style="padding: 16px; border-radius: 12px; background: rgba(46, 160, 67, 0.06); border: 1px solid rgba(46, 160, 67, 0.25); box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
            <h4 style="color:#56d364; margin-top:0; font-weight:700;">🟢 SECTOR SECURITY RATINGS: SECURE</h4>
            <p style="margin-bottom:0; font-size:0.9rem; color:rgba(255,255,255,0.75); line-height:1.45;">
                Operations are running at high safety rates. Target compliance margins have been successfully achieved. No emergency intervention is required at this node. Continue standard surveillance operations.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif compliance_score > 80:
        st.markdown("""
        <div style="padding: 16px; border-radius: 12px; background: rgba(210, 153, 34, 0.06); border: 1px solid rgba(210, 153, 34, 0.25); box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
            <h4 style="color:#e3b341; margin-top:0; font-weight:700;">🟡 SECTOR SECURITY RATINGS: CAUTION</h4>
            <p style="margin-bottom:0; font-size:0.9rem; color:rgba(255,255,255,0.75); line-height:1.45;">
                Compliance rates are currently within acceptable limits but show a slight downward trend. Peak breaches occur at <b>{high_risk_hour}</b>. We advise dispatching safety monitors during this hour to check PPE compliance.
            </p>
        </div>
        """.format(high_risk_hour=high_risk_hour), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding: 16px; border-radius: 12px; background: rgba(248, 81, 73, 0.06); border: 1px solid rgba(248, 81, 73, 0.25); box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
            <h4 style="color:#f85149; margin-top:0; font-weight:700;">🔴 SECTOR SECURITY RATINGS: RISK STATE</h4>
            <p style="margin-bottom:0; font-size:0.9rem; color:rgba(255,255,255,0.75); line-height:1.45;">
                <b>Critical safety levels breached!</b> Compliance Index has dropped to <b>{score:.1f}%</b>. High concentration of breaches logged. A review of site operations and safety vest audits is immediately recommended.
            </p>
        </div>
        """.format(score=compliance_score), unsafe_allow_html=True)

with col_s2:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">💾 Export Logs</h3>', unsafe_allow_html=True)
    if not df.empty:
        # Convert filtered df back to CSV representation
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 DOWNLOAD REPORT (CSV)",
            data=csv_data,
            file_name=f"aegis_safety_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No data available to export.")
