from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Lead:
    name: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    score: float = 0.0
    tier: str = "cold"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class ProspectorAgent:
    """Autonomous lead discovery and enrichment agent."""

    def __init__(self):
        self.processed = 0
        self.name = "Prospector"

    def enrich_lead(self, raw: dict) -> dict:
        """Enrich a raw lead dict with scored fields."""
        score = 50.0
        if raw.get("phone"):
            score += 20
        if raw.get("email"):
            score += 15
        score = min(score, 100.0)
        tier = "hot" if score > 80 else "warm" if score > 60 else "cold"
        self.processed += 1
        return {**raw, "score": score, "tier": tier}
