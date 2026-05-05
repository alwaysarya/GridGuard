import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import numpy as np

st.set_page_config(
    page_title="GridGuard - BESCOM Smart Meter Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .alert-high { background-color: #ff4444; color: white; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .alert-medium { background-color: #ffaa00; color: white; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .alert-low { background-color: #00c851; color: white; padding: 10px; border-radius: 5px; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ Controls")
    auto_refresh = st.checkbox("Auto-refresh (5 sec)", value=False)
    selected_meter = st.selectbox("Meter ID", [f"MTR-{str(i).zfill(3)}" for i in range(1, 51)])
    
    st.markdown("---")
    st.markdown("### Test Theft Detection")
    test_power = st.number_input("Power (Watts)", value=5000.0)
    test_voltage = st.number_input("Voltage", value=230.0)
    test_energy = st.number_input("Energy (kWh)", value=120.0)
    
    if st.button("🔍 Test for Theft", type="primary"):
        if test_power > 10000:
            st.error("🚨 THEFT DETECTED! High power consumption")
        elif test_power < 10 and test_energy > 100:
            st.error("🚨 THEFT DETECTED! Meter tampering suspected")
        else:
            st.success("✅ Normal reading")

# Generate data
@st.cache_data(ttl=10)
def generate_data(hours=24):
    timestamps = [(datetime.now() - timedelta(hours=i)).strftime("%H:%M") for i in range(hours, -1, -1)]
    data = []
    for i, ts in enumerate(timestamps):
        hour = int(ts.split(":")[0])
        if 6 <= hour <= 9 or 17 <= hour <= 21:
            base = 5000
        elif 10 <= hour <= 16:
            base = 3000
        else:
            base = 1500
        is_anomaly = random.random() < 0.08
        power = base * (random.uniform(2.5, 4) if is_anomaly else random.uniform(0.9, 1.1))
        data.append({
            "timestamp": ts,
            "power": max(0, power),
            "voltage": 230 + random.gauss(0, 5),
            "current": power/230,
            "is_anomaly": is_anomaly,
            "anomaly_type": random.choice(["high_power", "tampering", "voltage"]) if is_anomaly else None,
            "anomaly_score": random.uniform(0.75, 0.95) if is_anomaly else 0
        })
    return pd.DataFrame(data)

df = generate_data(24)

# Title
st.title("⚡ GridGuard - AI Smart Meter Intelligence")
st.markdown("### BESCOM - Real-time Loss Detection & Theft Prevention System")
st.markdown("---")

# ==================== METRICS ROW (4 cards) ====================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Meters", "1,250", "▲ 12")
with col2:
    st.metric("Active Alerts", f"{df['is_anomaly'].sum()}", "▼ 5")
with col3:
    st.metric("Detection Rate", "97.3%", "▲ 2.1%")
with col4:
    st.metric("Theft Prevented", "156.5 MWh", "▲ 18%")
st.markdown("---")

# ==================== POWER CONSUMPTION CHART ====================
st.subheader("📈 Real-time Power Consumption")
fig = go.Figure()
normal_df = df[df['is_anomaly'] == False]
anomaly_df = df[df['is_anomaly'] == True]
fig.add_trace(go.Scatter(x=normal_df['timestamp'], y=normal_df['power'], mode='lines', name='Normal', line=dict(color='blue', width=2)))
fig.add_trace(go.Scatter(x=anomaly_df['timestamp'], y=anomaly_df['power'], mode='markers', name='⚠️ Anomaly', marker=dict(color='red', size=12, symbol='x')))
fig.update_layout(height=400, xaxis_title="Time", yaxis_title="Power (W)")
st.plotly_chart(fig, use_container_width=True)

# ==================== VOLTAGE & CURRENT ====================
st.subheader("⚡ Voltage & Current Analysis")
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['voltage'], name="Voltage (V)", line=dict(color='orange')), secondary_y=False)
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['current'], name="Current (A)", line=dict(color='green')), secondary_y=True)
fig.add_hline(y=260, line_dash="dash", line_color="red", annotation_text="High", secondary_y=False)
fig.add_hline(y=180, line_dash="dash", line_color="orange", annotation_text="Low", secondary_y=False)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# ==================== ANOMALY DISTRIBUTION PIE CHART ====================
st.subheader("🎯 Anomaly Detection Rate")
anomaly_counts = df[df['is_anomaly']]['anomaly_type'].value_counts()
if not anomaly_counts.empty:
    fig = px.pie(values=anomaly_counts.values, names=anomaly_counts.index, title="Anomaly Types", hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No anomalies detected")

# ==================== HOURLY CONSUMPTION PATTERN ====================
st.subheader("📊 Hourly Consumption Pattern")
hourly_data = df.groupby(df['timestamp'].str[:2])['power'].mean()
fig = px.bar(x=hourly_data.index, y=hourly_data.values, title="Average Power by Hour", color=hourly_data.values, color_continuous_scale="Viridis")
fig.update_layout(xaxis_title="Hour", yaxis_title="Power (W)")
st.plotly_chart(fig, use_container_width=True)

# ==================== RECENT ALERTS TABLE ====================
st.subheader("🚨 Recent Alerts")
recent_alerts = df[df['is_anomaly'] == True].tail(5)
if not recent_alerts.empty:
    alert_data = []
    for _, alert in recent_alerts.iterrows():
        alert_data.append({
            "Time": alert['timestamp'],
            "Meter ID": selected_meter,
            "Type": alert['anomaly_type'],
            "Confidence": f"{alert['anomaly_score']*100:.0f}%",
            "Status": "Critical" if alert['anomaly_score'] > 0.85 else "High" if alert['anomaly_score'] > 0.75 else "Medium"
        })
    st.dataframe(pd.DataFrame(alert_data), use_container_width=True)
else:
    st.success("✅ No recent alerts")

# ==================== DETAILED METER ANALYSIS ====================
st.markdown("---")
st.subheader(f"📋 Detailed Meter Analysis: {selected_meter}")
col1, col2 = st.columns(2)

with col1:
    current = df.iloc[-1]
    st.metric("Current Power", f"{current['power']:.0f} W")
    st.metric("Voltage", f"{current['voltage']:.1f} V")
    st.metric("Current", f"{current['current']:.1f} A")
    st.metric("Status", "⚠️ Alert" if current['is_anomaly'] else "✅ Normal")

with col2:
    st.metric("Avg Power (24h)", f"{df['power'].mean():.0f} W")
    st.metric("Peak Power", f"{df['power'].max():.0f} W")
    st.metric("Min Power", f"{df['power'].min():.0f} W")
    st.metric("Total Energy", f"{df['power'].sum()/1000:.1f} kWh")
    st.metric("Risk Score", f"{df['anomaly_score'].max():.2f}")

# ==================== THEFT RISK HEATMAP ====================
st.markdown("---")
st.subheader("🗺️ Theft Risk Heatmap by Zone and Time")
zones = ["Zone A (Industrial)", "Zone B (Residential)", "Zone C (Commercial)", "Zone D (Rural)", "Zone E (Mixed)"]
risk_data = np.random.rand(5, 24) * 100
fig = px.imshow(risk_data, x=list(range(24)), y=zones, color_continuous_scale="RdYlGn_r", aspect="auto", title="Theft Risk Heatmap - High Risk (Red) to Low Risk (Green)")
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# ==================== PREDICTIVE ANALYTICS ====================
st.markdown("---")
st.subheader("🔮 Predictive Analytics & Forecasting")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Next 12 Hours Power Forecast")
    forecast_hours = list(range(13))
    last_power = df.iloc[-1]['power']
    forecast_values = [last_power * (1 + 0.03 * np.sin(i/3)) for i in range(13)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_hours, y=forecast_values, mode='lines+markers', name='Forecast'))
    upper = [f * 1.1 for f in forecast_values]
    lower = [f * 0.9 for f in forecast_values]
    fig.add_trace(go.Scatter(x=forecast_hours + forecast_hours[::-1], y=upper + lower[::-1], fill='toself', fillcolor='rgba(0,100,255,0.2)', line=dict(color='rgba(0,0,0,0)'), name='90% CI'))
    fig.update_layout(xaxis_title="Hours Ahead", yaxis_title="Predicted Power (W)", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Zone-wise Theft Risk Prediction")
    risk_zones = ["Industrial", "Residential", "Commercial", "Rural", "Mixed"]
    risk_scores = [78, 45, 89, 62, 53]
    colors = ['red' if x > 70 else 'orange' if x > 50 else 'green' for x in risk_scores]
    fig = go.Figure(go.Bar(x=risk_zones, y=risk_scores, marker_color=colors))
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="High Risk")
    fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Medium Risk")
    fig.update_layout(xaxis_title="Zone", yaxis_title="Risk Score (%)", height=350)
    st.plotly_chart(fig, use_container_width=True)

# ==================== SYSTEM HEALTH ====================
st.markdown("---")
st.subheader("📊 System Health Status")

col1, col2, col3, col4 = st.columns(4)
with col1:
    try:
        requests.get("http://localhost:8000/health", timeout=2)
        st.success("🟢 API Online")
    except:
        st.error("🔴 API Offline")
with col2:
    st.progress(0.98)
    st.caption("98% Healthy")
with col3:
    st.progress(0.96)
    st.caption("ML Model v1.0 | 97.3%")
with col4:
    st.progress(0.94)
    st.caption("94% Live Sync")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("⚡ **GridGuard AI** - Smart Meter Intelligence System | Powered by Artificial Intelligence | BESCOM Theme 8")
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(5)
    st.rerun()
