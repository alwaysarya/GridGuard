from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI(title="GridGuard AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MeterReading(BaseModel):
    meter_id: str
    timestamp: datetime
    voltage: float
    current: float
    power: float
    energy_consumed: float

@app.get("/")
async def root():
    return {"message": "GridGuard API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/v1/detection/detect-anomaly")
async def detect_anomaly(reading: MeterReading):
    is_anomaly = False
    anomaly_type = None
    score = 0.0
    
    if reading.power > 10000:
        is_anomaly = True
        anomaly_type = "high_power"
        score = 0.95
    elif reading.power < 10 and reading.energy_consumed > 100:
        is_anomaly = True
        anomaly_type = "tampering"
        score = 0.92
    elif reading.voltage < 180 or reading.voltage > 260:
        is_anomaly = True
        anomaly_type = "voltage"
        score = 0.85
    
    return {
        "meter_id": reading.meter_id,
        "is_anomaly": is_anomaly,
        "anomaly_score": score,
        "anomaly_type": anomaly_type,
        "message": "THEFT DETECTED!" if is_anomaly else "Normal",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
