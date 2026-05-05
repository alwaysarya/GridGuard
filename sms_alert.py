"""
GridGuard SMS Alert System
Automatically sends SMS when theft is detected
"""

import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# TextBee Configuration
DEVICE_ID = os.getenv("TEXTBEE_DEVICE_ID", "69fa6641b5cd3ce4c7f36f80")
API_KEY = os.getenv("TEXTBEE_API_KEY", "967240c9-6fe3-48b9-987c-539ad6a6b161")
ALERT_PHONE = os.getenv("ALERT_PHONE", "+917543907912")

def send_theft_alert(meter_id, theft_type, confidence, additional_info=""):
    """
    Send SMS alert for theft detection
    
    Args:
        meter_id: The meter where theft was detected
        theft_type: Type of theft (High Power, Tampering, etc.)
        confidence: Confidence score (0-100)
        additional_info: Extra details about the theft
    """
    
    # Build the message
    message = f"""🚨 GRIDGUARD THEFT ALERT!

📍 Meter: {meter_id}
🔍 Type: {theft_type}
📊 Confidence: {confidence}%
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{additional_info}
━━━━━━━━━━━━━━━━━━
⚡ ACTION: Immediate inspection required!

- GridGuard AI System"""

    # Send via TextBee
    url = f"https://api.textbee.dev/api/v1/gateway/devices/{DEVICE_ID}/send-sms"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    data = {"recipients": [ALERT_PHONE], "message": message}
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        success = response.status_code == 201 or response.status_code == 200
        if success:
            print(f"✅ SMS alert sent for meter {meter_id}")
        return success
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False

# Test function
if __name__ == "__main__":
    # Test the alert
    send_theft_alert("TEST-001", "High Power Consumption", 95, "Power: 15000W (normal: 5000W)")
