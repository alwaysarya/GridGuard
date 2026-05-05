from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Change this line
from .api.v1.endpoints import detection

app = FastAPI(
    title="GridGuard AI",
    version="1.0.0",
    description="AI for Smart Meter Intelligence & Loss Detection for BESCOM"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include detection routes
app.include_router(detection.router, prefix="/api/v1/detection", tags=["Anomaly Detection"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to GridGuard AI",
        "version": "1.0.0",
        "status": "operational",
        "project": "AI for Bharat - Theme 8: Smart Meter Intelligence"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "GridGuard AI"}
