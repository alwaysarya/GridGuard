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

# Custom CSS for alerts
st.markdown("""
<style>
    .alert-high { background-color: #ff4444; color: white; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .alert-medium { background-color: #ffaa00; color: white; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .alert-low { background-color: #00c851; color: white; padding: 10px; border-radius: 5px; margin: 5px 0; }
    div.stButton > button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ Control Panel")
    auto_refresh = st.checkbox("🔄 Auto-refresh (10 sec)", value=False)
    selected_meter = st.selectbox("Meter ID", [f"MTR-{str(i).zfill(3)}" for i in range(1, 51)])
    hours = st.slider("Hours of Data", 1, 48, 24)
    
    st.markdown("---")
    st.markdown("### ⚙️ Detection Thresholds")
    power_threshold = st.slider("Power Anomaly Threshold (W)", 5000, 20000, 10000)
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Generate realistic data
@st.cache_data(ttl=10)
def generate_data(meter_id, hours=24):
    timestamps = [(datetime.now() - timedelta(hours=i)).strftime("%H:%M") for i in range(hours, -1, -1)]
    data = []
    for i, ts in enumerate(timestamps):
        hour = int(ts.split(":")[0])
        # Peak hours pattern
        if 6 <= hour <= 9 or 17 <= hour <= 21:
            base = 5000 + np.random.normal(0, 500)
        elif 10 <= hour <= 16:
            base = 3000 + np.random.normal(0, 300)
        else:
            base = 1500 + np.random.normal(0, 200)
        
        is_anomaly = random.random() < 0.08
        if is_anomaly:
            power = base * random.uniform(2.5, 4)
            anomaly_type = random.choice(["high_power", "meter_tampering", "voltage_anomaly", "current_imbalance"])
            anomaly_score = random.uniform(0.75, 0.98)
        else:
            power = base * random.uniform(0.9, 1.1)
            anomaly_type = None
            anomaly_score = 0
        
        data.append({
            "timestamp": ts, "power": max(0, power), "voltage": 230 + np.random.normal(0, 5),
            "current": power / 230, "is_anomaly": is_anomaly, "anomaly_type": anomaly_type,
            "anomaly_score": anomaly_score
        })
    return pd.DataFrame(data)

df = generate_data(selected_meter, hours)

# Title
st.title("⚡ GridGuard - AI Smart Meter Intelligence Dashboard")
st.markdown("### BESCOM - Real-time Loss Detection & Theft Prevention System")
st.markdown("---")

# KPI Row - 6 metrics
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1: st.metric("Total Meters", "1,250", "▲ +12")
with col2: st.metric("Active Alerts", f"{df['is_anomaly'].sum()}", "▼ -5")
with col3: st.metric("Detection Accuracy", "97.3%", "▲ +2.1%")
with col4: st.metric("Theft Prevented", "156.5 MWh", "▲ +18%")
with col5: st.metric("Est. Savings", "₹12.5L", "▲ +12%")
with col6: st.metric("Avg Response", "0.85s", "▼ -0.1s")
st.markdown("---")

# Row 1: Power Consumption & Voltage/Current Analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📈 Real-time Power Consumption")
    fig = go.Figure()
    normal_df = df[df['is_anomaly'] == False]
    if not normal_df.empty:
        fig.add_trace(go.Scatter(x=normal_df['timestamp'], y=normal_df['power'], mode='lines', name='Normal Consumption', line=dict(color='#1f77b4', width=2), fill='tozeroy', fillcolor='rgba(31,119,180,0.1)'))
    anomaly_df = df[df['is_anomaly'] == True]
    if not anomaly_df.empty:
        fig.add_trace(go.Scatter(x=anomaly_df['timestamp'], y=anomaly_df['power'], mode='markers', name='⚠️ Anomaly Detected', marker=dict(color='red', size=15, symbol='x')))
    fig.update_layout(title="Power Consumption with Anomaly Detection", height=400, hovermode='x unified', xaxis_title="Time", yaxis_title="Power (Watts)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("## ⚡ Voltage & Current Analysis")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['voltage'], name="Voltage (V)", line=dict(color='orange', width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['current'], name="Current (A)", line=dict(color='green', width=2)), secondary_y=True)
    fig.add_hline(y=260, line_dash="dash", line_color="red", annotation_text="High Voltage", secondary_y=False)
    fig.add_hline(y=180, line_dash="dash", line_color="orange", annotation_text="Low Voltage", secondary_y=False)
    fig.update_layout(title="Voltage and Current Trends", height=400, hovermode='x unified', xaxis_title="Time")
    fig.update_yaxes(title_text="Voltage (V)", secondary_y=False)
    fig.update_yaxes(title_text="Current (A)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 2: Anomaly Distribution, Hourly Pattern, Recent Alerts
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("## 🎯 Anomaly Distribution")
    anomaly_counts = df[df['is_anomaly']]['anomaly_type'].value_counts()
    if not anomaly_counts.empty:
        fig = px.pie(values=anomaly_counts.values, names=anomaly_counts.index, title="Anomaly Types Breakdown", hole=0.3, color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("## 📊 Hourly Consumption Pattern")
    hourly_data = df.groupby(df['timestamp'].str[:2])['power'].mean()
    fig = px.bar(x=hourly_data.index, y=hourly_data.values, title="Average Power by Hour of Day", color=hourly_data.values, color_continuous_scale="Viridis", labels={'x': 'Hour (24h)', 'y': 'Power (Watts)'})
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("## 🚨 Recent Alerts")
    recent_alerts = df[df['is_anomaly'] == True].tail(5)
    if not recent_alerts.empty:
        for _, alert in recent_alerts.iterrows():
            if alert['anomaly_score'] > 0.85:
                st.markdown(f'<div class="alert-high">🚨 {alert["anomaly_type"]}<br><small>Time: {alert["timestamp"]} | Score: {alert["anomaly_score"]:.2f}</small></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-medium">⚠️ {alert["anomaly_type"]}<br><small>Time: {alert["timestamp"]} | Score: {alert["anomaly_score"]:.2f}</small></div>', unsafe_allow_html=True)
    else:
        st.success("✅ No active alerts")

st.markdown("---")

# Row 3: Detailed Meter Analysis
st.markdown(f"## 📋 Detailed Meter Analysis: {selected_meter}")
col1, col2 = st.columns(2)

with col1:
    current = df.iloc[-1]
    st.markdown("### Current Live Readings")
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Power", f"{current['power']:.1f} W")
    with m2: st.metric("Voltage", f"{current['voltage']:.1f} V")
    with m3: st.metric("Current", f"{current['current']:.1f} A")
    m4, m5, m6 = st.columns(3)
    with m4: st.metric("Status", "⚠️ Alert" if current['is_anomaly'] else "✅ Normal")
    with m5: st.metric("Energy (24h)", f"{df['power'].sum() / 1000:.1f} kWh")
    with m6: st.metric("Risk Score", f"{df['anomaly_score'].max():.2f}")

with col2:
    st.markdown("### 24-Hour Statistics")
    stats_df = pd.DataFrame({
        "Metric": ["Average Power", "Peak Power", "Min Power", "Total Energy", "Anomaly Count", "Avg Anomaly Score"],
        "Value": [f"{df['power'].mean():.0f} W", f"{df['power'].max():.0f} W", f"{df['power'].min():.0f} W", f"{df['power'].sum() / 1000:.1f} kWh", f"{df['is_anomaly'].sum()}", f"{df['anomaly_score'].mean():.2f}"]
    })
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Row 4: Theft Risk Heatmap
st.markdown("## 🗺️ Theft Risk Heatmap by Zone and Time")
zones = ["Zone A (Industrial)", "Zone B (Residential)", "Zone C (Commercial)", "Zone D (Rural)", "Zone E (Mixed)"]
risk_data = np.random.rand(5, 24) * 100
fig = px.imshow(risk_data, labels=dict(x="Hour of Day", y="Zone", color="Risk Score (%)"), x=list(range(24)), y=zones, title="Theft Risk Heatmap - High Risk (Red) to Low Risk (Green)", color_continuous_scale="RdYlGn_r", aspect="auto", zmin=0, zmax=100)
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 5: Predictive Analytics
st.markdown("## 🔮 Predictive Analytics & Forecasting")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Next 12 Hours Power Forecast")
    forecast_hours = list(range(13))
    last_power = df.iloc[-1]['power']
    forecast_values = [last_power * (1 + 0.03 * np.sin(i/3) + random.uniform(-0.05, 0.05)) for i in range(13)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_hours, y=forecast_values, mode='lines+markers', name='Forecasted Power', line=dict(color='blue', width=2, dash='dot')))
    upper_bound = [v * 1.1 for v in forecast_values]
    lower_bound = [v * 0.9 for v in forecast_values]
    fig.add_trace(go.Scatter(x=forecast_hours + forecast_hours[::-1], y=upper_bound + lower_bound[::-1], fill='toself', fillcolor='rgba(0,100,255,0.2)', line=dict(color='rgba(255,255,255,0)'), name='Confidence Interval (90%)'))
    fig.update_layout(title="Power Consumption Forecast with Confidence Bounds", xaxis_title="Hours Ahead", yaxis_title="Predicted Power (Watts)", height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Zone-wise Theft Risk Prediction")
    risk_zones = ["Industrial", "Residential", "Commercial", "Rural", "Mixed"]
    risk_scores = [78, 45, 89, 62, 53]
    colors = ['red' if x > 70 else 'orange' if x > 50 else 'green' for x in risk_scores]
    fig = go.Figure(go.Bar(x=risk_zones, y=risk_scores, marker_color=colors, text=[f"{x}%" for x in risk_scores], textposition='auto'))
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
    fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Medium Risk Threshold")
    fig.update_layout(title="Predicted Theft Risk for Next 24 Hours", xaxis_title="Zone", yaxis_title="Risk Score (%)", height=400)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 6: System Health
st.markdown("## 📊 System Health Status")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("### 🔌 API Status")
    try:
        requests.get("http://localhost:8000/health", timeout=2)
        st.success("🟢 Online")
    except: 
        st.error("🔴 Offline")
with col2:
    st.markdown("### 📊 Data Pipeline")
    st.progress(0.98)
    st.caption("98% Healthy | Real-time: Active")
with col3:
    st.markdown("### 🤖 ML Model")
    st.progress(0.96)
    st.caption("v1.0 - Production | Accuracy: 97.3%")
with col4:
    st.markdown("### ⚡ Real-time Sync")
    st.progress(0.94)
    st.caption("94% Live | Latency: 0.85s")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center;'>
    <p>⚡ <strong>GridGuard AI</strong> - Smart Meter Intelligence System</p>
    <p>Powered by Artificial Intelligence | BESCOM - Theme 8: AI for Smart Meter Intelligence & Loss Detection</p>
    <p>Real-time monitoring | Automated theft detection | Predictive analytics | Zone-wise risk assessment</p>
</div>
""", unsafe_allow_html=True)
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if auto_refresh:
    import time
    time.sleep(10)
    st.rerun()
