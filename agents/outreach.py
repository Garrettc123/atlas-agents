"""
ATLAS Outreach Agent
Role: Personalized Multi-Channel Message Generation
Compliance: TCPA + CAN-SPAM built in
"""

from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from typing import Dict
from datetime import datetime
import pytz
import os
import logging

logger = logging.getLogger(__name__)

# Texas-safe hours (strictest standard)
ALLOWED_HOURS_START = 9   # 9 AM
ALLOWED_HOURS_END = 21    # 9 PM

OPT_OUT_KEYWORDS = {
    'STOP', 'QUIT', 'CANCEL', 'UNSUBSCRIBE',
    'OPT OUT', 'REMOVE', 'END', 'LEAVE'
}


def is_allowed_send_time(timezone_str: str = 'America/Chicago') -> bool:
    """Check if current time is within TCPA-compliant send window."""
    tz = pytz.timezone(timezone_str)
    local_now = datetime.now(tz)
    return ALLOWED_HOURS_START <= local_now.hour < ALLOWED_HOURS_END


def is_opt_out_message(text: str) -> bool:
    """Detect opt-out keywords (TCPA compliance)."""
    upper = text.upper().strip()
    return any(kw in upper for kw in OPT_OUT_KEYWORDS)


class OutreachAgent:
    """Generates TCPA/CAN-SPAM compliant personalized outreach messages."""

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7,
        )
        self.agent = Agent(
            role="Outreach Specialist",
            goal="Craft personalized, high-converting compliant outreach messages",
            backstory=(
                "Expert at contractor outreach copy. Emergency repairs need speed and "
                "reassurance. Exploratory leads need education and social proof. "
                "You keep SMS under 160 chars and emails under 150 words. "
                "You always include clear CTAs and never use deceptive language."
            ),
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

    def generate_outreach(self, lead: Dict, channel: str = 'sms',
                          client_name: str = 'your roofing contractor') -> Dict:
        """
        Generates compliant outreach message.

        Args:
            lead: Enriched + qualified lead dict
            channel: 'sms' | 'email'
            client_name: Contractor's business name for disclosure

        Returns:
            {channel, subject (email only), message, cta, compliant, blocked_reason}
        """
        # Time compliance check
        if not is_allowed_send_time():
            logger.warning(f"Message blocked — outside send window for {lead.get('name')}")
            return {
                'channel': channel,
                'compliant': False,
                'blocked_reason': 'outside_send_window',
                'message': None,
            }

        ai_disclosure = f"(AI-assisted msg from {client_name})"

        if channel == 'sms':
            prompt = f"""Write a personalized TCPA-compliant SMS for this contractor lead.

            Lead name: {lead.get('name')}
            Urgency: {lead.get('urgency', 'standard')}
            Pain points: {lead.get('pain_points', [])}
            Tier: {lead.get('tier', 'warm')}

            Requirements:
            - Max 155 characters (leave room for opt-out instruction)
            - Address specific issue mentioned
            - Offer immediate value (free inspection / same-day service)
            - End with: Reply STOP to opt out
            - MUST include AI disclosure snippet: {ai_disclosure}

            Return the SMS text ONLY."""
        else:
            prompt = f"""Write a personalized CAN-SPAM compliant email for this contractor lead.

            Lead name: {lead.get('name')}
            Urgency: {lead.get('urgency', 'standard')}
            Pain points: {lead.get('pain_points', [])}
            Job size: {lead.get('estimated_job_size', 'medium')}
            Client: {client_name}

            Requirements:
            - Subject line: max 8 words, honest (no deception)
            - Body: max 150 words
            - Include physical address placeholder: {{CLIENT_ADDRESS}}
            - Include unsubscribe: Reply UNSUBSCRIBE to stop
            - Include AI disclosure: {ai_disclosure}
            - Strong CTA (book inspection / call now)

            Return JSON: {{subject: str, body: str}}"""

        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="Message content",
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=False)
        result = crew.kickoff()

        logger.info(f"Outreach generated: {channel} for {lead.get('name')}")
        return {
            'channel': channel,
            'message': str(result),
            'compliant': True,
            'blocked_reason': None,
            'lead_id': lead.get('id'),
        }

    @staticmethod
    def handle_inbound_reply(message: str, lead_id: str, db=None) -> Dict:
        """
        Processes inbound reply. Handles opt-outs immediately (TCPA).

        Returns: {action: 'opted_out' | 'continue_conversation', confirmation: str}
        """
        if is_opt_out_message(message):
            if db:
                db.suppress_lead(lead_id)
            logger.info(f"Lead {lead_id} opted out via keyword")
            return {
                'action': 'opted_out',
                'confirmation': 'You have been unsubscribed. Reply START to rejoin.',
            }
        return {'action': 'continue_conversation', 'confirmation': None}


if __name__ == "__main__":
    import json

    sample = {
        'id': 'lead_001',
        'name': 'John Martinez',
        'urgency': 'emergency',
        'pain_points': ['storm damage', 'active roof leak'],
        'tier': 'hot',
        'estimated_job_size': 'large',
    }

    agent = OutreachAgent()
    sms = agent.generate_outreach(sample, channel='sms', client_name='DFW Roofing Pro')
    email = agent.generate_outreach(sample, channel='email', client_name='DFW Roofing Pro')

    print("SMS:", json.dumps(sms, indent=2, default=str))
    print("\nEmail:", json.dumps(email, indent=2, default=str))
