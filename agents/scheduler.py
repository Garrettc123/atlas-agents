class SchedulerAgent:
    """Appointment booking agent."""

    def __init__(self):
        self.processed = 0
        self.name = "Scheduler"

    def book(self, lead: dict) -> dict:
        self.processed += 1
        return {**lead, "appointment": "pending_confirmation", "calendar_invite": True}
