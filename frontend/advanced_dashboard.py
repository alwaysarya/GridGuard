import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import numpy as np

st.set_page_config(page_title="GridGuard AI", layout="wide")

st.title("⚡ GridGuard - AI Smart Meter Intelligence")
st.markdown("### Real-time Theft Detection System for BESCOM")

# Sidebar
with st.sidebar:
    st.header("🎮 Controls")
    auto_refresh = st.checkbox("Auto-refresh (5 sec)", value=False)
    meter_id = st.selectbox("Meter ID", [f"MTR-{i:03d}" for i in range(1, 51)])
    
    st.header("⚙️ Test Theft Detection")
    power = st.number_input("Power (Watts)", value=5000.0)
    voltage = st.number_input("Voltage", value=230.0)
    energy = st.number_input("Energy (kWh)", value=120.0)
    
    if st.button("🔍 Test for Theft", type="primary"):
        payload = {
            "meter_id": meter_id,
            "timestamp": datetime.now().isoformat(),
            "voltage": voltage,
            "current": power/voltage,
            "power": power,
            "energy_consumed": energy
        }
        try:
            response = requests.post("http://localhost:8000/api/v1/detection/detect-anomaly", json=payload)
            result = response.json()
            if result["is_anomaly"]:
                st.error(f"🚨 {result['message']}")
                st.warning(f"Confidence: {result['anomaly_score']*100}%")
                st.info(f"Type: {result['anomaly_type']}")
            else:
                st.success(f"✅ {result['message']}")
        except:
            st.error("Backend not running! Start with: python3 backend/app.py")

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Meters", "1,250", "▲ 12")
with col2:
    st.metric("Active Alerts", "23", "▼ 5")
with col3:
    st.metric("Detection Rate", "97.3%", "▲ 2.1%")
with col4:
    st.metric("Theft Prevented", "156.5 MWh", "▲ 18%")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Real-time Power Consumption")
    hours = list(range(24))
    consumption = [120, 95, 80, 75, 70, 85, 150, 230, 280, 310, 290, 270,
                   260, 255, 280, 350, 420, 380, 340, 310, 280, 240, 180, 140]
    fig = px.line(x=hours, y=consumption, title="Power Consumption Pattern")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Anomaly Detection Rate")
    categories = ['High Power', 'Tampering', 'Voltage', 'Current']
    values = [45, 28, 32, 15]
    fig = px.pie(values=values, names=categories, title="Anomaly Types")
    st.plotly_chart(fig, use_container_width=True)

# Alerts Table
st.subheader("🚨 Recent Alerts")
alerts_data = {
    "Time": ["14:32", "14:28", "14:15", "13:58", "13:42"],
    "Meter ID": ["MTR-045", "MTR-012", "MTR-089", "MTR-034", "MTR-067"],
    "Type": ["High Power", "Tampering", "Voltage", "High Power", "Current"],
    "Confidence": ["95%", "88%", "82%", "91%", "76%"],
    "Status": ["Critical", "High", "Medium", "Critical", "Medium"]
}
st.dataframe(alerts_data, use_container_width=True)

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(5)
    st.rerun()

    # ============ NEW FEATURES ADDED BELOW ============

# Feature 3: Anomaly Distribution Pie Chart
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("## 🎯 Anomaly Distribution")
    anomaly_counts = df[df['is_anomaly']]['anomaly_type'].value_counts()
    if not anomaly_counts.empty:
        fig = px.pie(values=anomaly_counts.values, names=anomaly_counts.index, title="Anomaly Types Breakdown", hole=0.3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

# Feature 4: Hourly Consumption Pattern
with col2:
    st.markdown("## 📊 Hourly Consumption Pattern")
    hourly_data = df.groupby(df['timestamp'].str[:2])['power'].mean()
    fig = px.bar(x=hourly_data.index, y=hourly_data.values, title="Average Power by Hour of Day", color=hourly_data.values, color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)

# Feature 5: Recent Alerts Box
with col3:
    st.markdown("## 🚨 Recent Alerts")
    recent_alerts = df[df['is_anomaly'] == True].tail(5)
    if not recent_alerts.empty:
        for _, alert in recent_alerts.iterrows():
            if alert['anomaly_score'] > 0.85:
                st.error(f"🚨 {alert['anomaly_type']} - {alert['anomaly_score']*100:.0f}%")
            else:
                st.warning(f"⚠️ {alert['anomaly_type']} - {alert['anomaly_score']*100:.0f}%")
    else:
        st.success("✅ No alerts")

# Feature 6: Theft Risk Heatmap
st.markdown("---")
st.markdown("## 🗺️ Theft Risk Heatmap by Zone and Time")
zones = ["Zone A (Industrial)", "Zone B (Residential)", "Zone C (Commercial)", "Zone D (Rural)", "Zone E (Mixed)"]
risk_data = np.random.rand(5, 24) * 100
fig = px.imshow(risk_data, labels=dict(x="Hour of Day", y="Zone", color="Risk Score (%)"), x=list(range(24)), y=zones, color_continuous_scale="RdYlGn_r", aspect="auto")
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Feature 7: Predictive Analytics
st.markdown("---")
st.markdown("## 🔮 Predictive Analytics & Forecasting")

c1, c2 = st.columns(2)

with c1:
    st.markdown("### Next 12 Hours Power Forecast")
    forecast_hours = list(range(13))
    last_power = df.iloc[-1]['power']
    forecast_values = [last_power * (1 + 0.03 * np.sin(i/3)) for i in range(13)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_hours, y=forecast_values, mode='lines+markers', name='Forecasted Power'))
    fig.update_layout(title="Power Consumption Forecast", xaxis_title="Hours Ahead", yaxis_title="Predicted Power (Watts)")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### Zone-wise Theft Risk Prediction")
    risk_zones = ["Industrial", "Residential", "Commercial", "Rural", "Mixed"]
    risk_scores = [78, 45, 89, 62, 53]
    fig = px.bar(x=risk_zones, y=risk_scores, title="Predicted Theft Risk", color=risk_scores, color_continuous_scale="RdYlGn_r")
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.update_layout(xaxis_title="Zone", yaxis_title="Risk Score (%)")
    st.plotly_chart(fig, use_container_width=True)

# Feature 8: System Health
st.markdown("---")
st.markdown("## 📊 System Health Status")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("API Status", "🟢 Online")
with col2:
    st.metric("Data Pipeline", "98%")
with col3:
    st.metric("ML Model", "97.3%")
with col4:
    st.metric("Real-time Sync", "94%")
