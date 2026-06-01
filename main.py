from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ATLAS Agent API",
    description="Autonomous Transaction & Lead Automation System - Garcar Enterprise",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "operational",
        "system": "ATLAS",
        "company": "Garcar Enterprise",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": [
            "prospector",
            "qualifier",
            "outreach",
            "conversation",
            "scheduler",
            "revenue",
            "analytics",
        ],
    }


@app.get("/agents/status")
async def agent_status():
    return {
        "prospector": {"status": "active", "processed": 0},
        "outreach": {"status": "active", "processed": 0},
        "scheduler": {"status": "active", "processed": 0},
    }


@app.post("/leads/intake")
async def intake_lead(payload: dict):
    """Receive a new lead and route through ATLAS pipeline."""
    return {"status": "queued", "lead_id": "atlas-" + str(hash(str(payload)))[-8:]}
