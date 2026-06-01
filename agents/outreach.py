"""
ATLAS Outreach Agent
TCPA-compliant SMS/email outreach with opt-out enforcement.
"""
import re
from datetime import datetime, time
from typing import Optional

OPT_OUT_KEYWORDS = {"stop", "unsubscribe", "cancel", "quit", "end", "optout", "opt-out"}
SEND_WINDOW_START = time(8, 0)   # 8:00 AM local
SEND_WINDOW_END = time(20, 0)    # 8:00 PM local


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
        return bool(words & OPT_OUT_KEYWORDS)

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
