import streamlit as st
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DEVICE_ID = os.getenv("TEXTBEE_DEVICE_ID", "69fa6641b5cd3ce4c7f36f80")
API_KEY = os.getenv("TEXTBEE_API_KEY", "967240c9-6fe3-48b9-987c-539ad6a6b161")
DEFAULT_PHONE = os.getenv("TEST_PHONE_NUMBER", "+917543907912")

def send_sms_alert(phone, meter_id, theft_type, confidence):
    """Send SMS alert via TextBee"""
    message = f"""🚨 GRIDGUARD THEFT ALERT!

Meter: {meter_id}
Type: {theft_type}
Confidence: {confidence}%
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ACTION: Immediate inspection required!"""

    url = f"https://api.textbee.dev/api/v1/gateway/devices/{DEVICE_ID}/send-sms"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    data = {"recipients": [phone], "message": message}
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        return response.status_code == 200 or response.json().get("success", False)
    except:
        return False

# Add this function to your existing dashboard
def show_sms_panel():
    st.markdown("### 📱 Send SMS Alert")
    
    col1, col2 = st.columns(2)
    with col1:
        phone = st.text_input("Phone Number", value=DEFAULT_PHONE, key="sms_phone")
        meter = st.text_input("Meter ID", value="MTR-001", key="sms_meter")
    with col2:
        theft = st.selectbox("Theft Type", ["High Power", "Meter Tampering", "Voltage Anomaly"], key="sms_type")
        confidence = st.slider("Confidence %", 50, 100, 95, key="sms_conf")
    
    if st.button("📱 Send Alert SMS", type="primary", key="send_sms_btn"):
        if send_sms_alert(phone, meter, theft, confidence):
            st.success("✅ SMS sent successfully!")
            st.balloons()
        else:
            st.error("❌ Failed to send SMS")

# Run standalone
if __name__ == "__main__":
    st.set_page_config(page_title="GridGuard SMS", page_icon="📱")
    st.title("📱 GridGuard SMS Alert System")
    show_sms_panel()
