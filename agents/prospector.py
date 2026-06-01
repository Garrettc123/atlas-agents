"""
ATLAS Prospector Agent
Role: Lead Identification & Enrichment
Framework: CrewAI + Claude Sonnet 4
"""

from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from typing import Dict, List
import os
import logging

logger = logging.getLogger(__name__)


class ProspectorAgent:
    """Enriches raw lead data with property context, urgency, and job sizing."""

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.3,
        )
        self.agent = Agent(
            role="Lead Prospector",
            goal="Identify high-value contractor leads and enrich with actionable context",
            backstory=(
                "Expert in DFW contractor markets. You understand emergency roofing patterns, "
                "seasonal demand, commercial vs residential signals, and geographic nuances "
                "across Dallas-Fort Worth. Your enrichment data drives accurate qualification."
            ),
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

    def enrich_lead(self, lead_data: Dict) -> Dict:
        """
        Enriches a raw lead with contextual data.

        Args:
            lead_data: {name, email, phone, address, message, source}

        Returns:
            Enriched dict with: property_type, urgency, estimated_job_size,
            geographic_zone, pain_points, buying_signals, best_contact_time
        """
        task = Task(
            description=f"""Analyze this contractor lead and return enrichment data as JSON:

            Lead Data:
            {lead_data}

            Return a JSON object with exactly these keys:
            - property_type: 'residential' | 'commercial'
            - urgency: 'emergency' | 'standard' | 'exploratory'
            - estimated_job_size: 'small' (<$5K) | 'medium' ($5-15K) | 'large' (>$15K)
            - geographic_zone: DFW sub-region
            - pain_points: list of specific issues mentioned
            - buying_signals: list of urgency/budget/timeline indicators
            - best_contact_time: 'morning' | 'afternoon' | 'evening'
            """,
            agent=self.agent,
            expected_output="JSON object with enrichment fields",
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=False)
        result = crew.kickoff()

        logger.info(f"Lead enriched: {lead_data.get('name')} — urgency detected")
        return {**lead_data, "enrichment": str(result)}

    def batch_enrich(self, leads: List[Dict]) -> List[Dict]:
        """Batch enrich multiple leads."""
        return [self.enrich_lead(lead) for lead in leads]


if __name__ == "__main__":
    import json

    sample = {
        "name": "John Martinez",
        "email": "john@example.com",
        "phone": "214-555-0123",
        "address": "1234 Oak St, Dallas TX 75201",
        "message": "Storm damage last night — water leaking into master bedroom, need help ASAP",
        "source": "website_form",
    }

    agent = ProspectorAgent()
    result = agent.enrich_lead(sample)
    print(json.dumps(result, indent=2, default=str))
