class AnalyticsAgent:
    """Performance tracking and reporting."""

    def __init__(self):
        self.processed = 0
        self.name = "Analytics"

    def report(self, pipeline: list) -> dict:
        self.processed += 1
        total = len(pipeline)
        converted = sum(1 for lead in pipeline if lead.get("paid"))
        return {
            "total_leads": total,
            "converted": converted,
            "conversion_rate": round(converted / total * 100, 1) if total else 0,
        }
