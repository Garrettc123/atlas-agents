class QualifierAgent:
    """Qualifies enriched leads before outreach."""

    def __init__(self):
        self.processed = 0
        self.name = "Qualifier"

    def qualify(self, lead: dict) -> dict:
        """Return lead with qualification verdict."""
        qualified = lead.get("score", 0) >= 50
        self.processed += 1
        return {**lead, "qualified": qualified}
