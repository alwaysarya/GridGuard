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
