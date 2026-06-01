import re
from datetime import datetime, time
from typing import Optional

OPT_OUT_KEYWORDS = {
    "STOP",
    "QUIT",
    "CANCEL",
    "UNSUBSCRIBE",
    "OPT OUT",
    "REMOVE",
    "END",
    "LEAVE",
}
SEND_WINDOW_START = time(8, 0)  # 8:00 AM local
SEND_WINDOW_END = time(20, 0)  # 8:00 PM local


def is_opt_out_message(message: str) -> bool:
    """Returns True if message contains an opt-out keyword."""
    normalized = message.strip().upper()
    return any(keyword in normalized for keyword in OPT_OUT_KEYWORDS)


def is_allowed_send_time(timezone_str: str = "America/Chicago") -> bool:
    """Check if current time is within TCPA-compliant send window."""
    now = datetime.now().time()
    return SEND_WINDOW_START <= now <= SEND_WINDOW_END


class OutreachAgent:
    """TCPA-compliant outreach with time-window and opt-out enforcement."""

    def __init__(self):
        self.opt_out_list: set[str] = set()
        self.processed = 0
        self.name = "Outreach"

    def is_opted_out(self, phone: str) -> bool:
        normalized = re.sub(r"\D", "", phone)
        return normalized in self.opt_out_list

    def is_send_window(self, local_time: Optional[datetime] = None) -> bool:
        now = (local_time or datetime.now()).time()
        return SEND_WINDOW_START <= now <= SEND_WINDOW_END

    def detect_opt_out(self, message: str) -> bool:
        words = set(message.lower().split())
        return bool(words & {k.lower() for k in OPT_OUT_KEYWORDS})

    def handle_reply(self, phone: str, message: str) -> str:
        if self.detect_opt_out(message):
            normalized = re.sub(r"\D", "", phone)
            self.opt_out_list.add(normalized)
            return "opted_out"
        return "active"

    async def send(self, phone: str, message: str) -> dict:
        if self.is_opted_out(phone):
            return {"status": "blocked", "reason": "opted_out"}
        if not self.is_send_window():
            return {"status": "queued", "reason": "outside_send_window"}
        self.processed += 1
        return {"status": "sent", "phone": phone}

    def generate_outreach(
        self,
        lead: dict,
        channel: str = "sms",
        client_name: str = "your roofing contractor",
    ) -> dict:
        """Generate compliant outreach message for lead."""
        if not is_allowed_send_time():
            return {
                "channel": channel,
                "compliant": False,
                "blocked_reason": "outside_send_window",
                "message": None,
            }
        return {
            "channel": channel,
            "message": f"Hi {lead.get('name')}, this is {client_name}.",
            "compliant": True,
            "blocked_reason": None,
            "lead_id": lead.get("id"),
        }

    @staticmethod
    def handle_inbound_reply(message: str, lead_id: str, db=None) -> dict:
        """Process inbound reply - enforce opt-out immediately."""
        if is_opt_out_message(message):
            if db:
                db.suppress_lead(lead_id)
            return {
                "action": "opted_out",
                "confirmation": "You have been unsubscribed. Reply START to rejoin.",
            }
        return {"action": "continue_conversation", "confirmation": None}
