class ConversationAgent:
    """Dialogue management and objection handling."""
    def __init__(self):
        self.processed = 0
        self.name = "Conversation"

    def handle(self, lead: dict, message: str) -> dict:
        self.processed += 1
        return {**lead, "conversation_status": "active", "last_reply": message}
