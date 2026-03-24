import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# -------- CONFIG --------
LOG_PATH = "violations.csv"
CHART_THEME = "plotly_dark"
TIME_GROUP = "hour"

# -------- SAFE LOADER --------
def load_logs():
    if not os.path.exists(LOG_PATH):
        return pd.DataFrame()
    try:
        df = pd.read_csv(LOG_PATH)
        if df.empty: return df
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except Exception as e:
        st.error(f"Error loading logs: {e}")
        return pd.DataFrame()

def compute_metrics(df):
    if df.empty: return 0, 0, 0, 0
    total = len(df)
    compliant = len(df[df["status"] == "Safe"])
    violations = len(df[df["status"] == "Violation"])
    compliance_percent = (compliant / total * 100) if total else 0
    return total, compliant, violations, compliance_percent

def trend_data(df, group="hour"):
    if df.empty: return pd.DataFrame()
    if group == "hour":
        df["time_group"] = df["timestamp"].dt.hour
    elif group == "day":
        df["time_group"] = df["timestamp"].dt.date
    else:
        df["time_group"] = df["timestamp"].dt.strftime("%H:%M")
    
    trend = df.groupby("time_group")["status"].apply(lambda x: (x == "Violation").sum()).reset_index(name="violations")
    return trend

def render_dashboard():
    st.markdown('<h1 style="color:#1e3a8a;">📊 Strategic Safety Intelligence</h1>', unsafe_allow_html=True)
    st.markdown("---")

    df = load_logs()
    if df.empty:
        st.info("💡 **Awaiting Data Initialization.** Start detection on a dashboard to gather safety metrics.")
        st.info("💡 **Navigation View:** Use the sidebar to return to the monitoring terminal.")
        return

    # metrics
    total, compliant, violations, compliance_percent = compute_metrics(df)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Observations", total)
    k2.metric("Safe", compliant)
    k3.metric("Breaches", violations)
    k4.metric("Compliance", f"{compliance_percent:.1f}%")

    st.markdown("---")
    
    # charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚠️ Violation Types")
        if "violation_type" in df.columns:
            v_counts = df[df["status"] == "Violation"]["violation_type"].value_counts().reset_index()
            v_counts.columns = ["Type", "Count"]
            fig1 = px.pie(v_counts, names="Type", values="Count", hole=0.3)
            st.plotly_chart(fig1, use_container_width=True)
    
    with c2:
        st.subheader("👷 Worker Safety")
        if "worker_id" in df.columns:
            w_viols = df[df["status"] == "Violation"].groupby("worker_id").size().reset_index(name="Count")
            fig2 = px.bar(w_viols, x="worker_id", y="Count", color="Count", color_continuous_scale="Reds")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 AegisAI Safety Insights")
    
    i_col, t_col = st.columns([1, 2])
    with i_col:
        st.markdown('<div style="background:#f0f7ff; padding:15px; border-radius:10px; border-left:5px solid #1e3a8a; color:#333;">', unsafe_allow_html=True)
        st.markdown("#### **Analysis Report**")
        if violations > 0:
            st.warning(f"🚨 **Risk Detected:** {violations} safety breaches recorded.")
            if compliance_percent < 85:
                st.error("📉 **Attention Required:** Compliance is below target safety levels.")
        else:
            st.success("✅ **Perfect Compliance:** Operations are currently stable.")
        st.info("📝 **Advice:** Regular PPE audits are recommended.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with t_col:
        trend = trend_data(df)
        if not trend.empty:
            fig_t = px.area(trend, x="time_group", y="violations", title="Hourly Breach Intensity")
            st.plotly_chart(fig_t, use_container_width=True)

    st.markdown("---")
    st.info("💡 **Navigation View:** Use the sidebar to return to the monitoring terminal.")

if __name__ == "__main__":
    render_dashboard()
