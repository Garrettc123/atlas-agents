"""
ATLAS Qualifier Agent
Role: Lead Scoring & Prioritization (0-100)
Framework: CrewAI + Weighted Rubric
"""

from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic
from typing import Dict
import os
import logging

logger = logging.getLogger(__name__)

SCORING_RUBRIC = """
Scoring Rubric (100 points total):
- Urgency     (35 pts): emergency=35, standard=20, exploratory=5
- Budget      (25 pts): explicit mention=25, implied=15, none=0
- Job Size    (20 pts): large(>$15K)=20, medium($5-15K)=15, small(<$5K)=10
- Geography   (10 pts): core DFW service area=10, fringe=5, outside=0
- Contact     (10 pts): phone+email=10, phone only=7, email only=5
"""


class QualifierAgent:
    """Scores leads 0-100. Hot=80+, Warm=60-79, Cold=<60."""

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.2,
        )
        self.agent = Agent(
            role="Lead Qualifier",
            goal="Score contractor leads 0-100 and recommend next action",
            backstory=(
                "Expert at roofing lead qualification. Emergency repairs convert at 80%+. "
                "Exploratory 'just looking' leads convert at <20%. You use the weighted "
                "rubric precisely and explain each score component."
            ),
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

    def score_lead(self, enriched_lead: Dict) -> Dict:
        """
        Returns scored lead dict with: score, tier, reasoning,
        recommended_action, priority (1=highest)
        """
        task = Task(
            description=f"""Score this contractor lead using the rubric. Return JSON.

            Lead Data:
            {enriched_lead}

            {SCORING_RUBRIC}

            Return JSON with:
            - score: int 0-100
            - tier: 'hot' (80+) | 'warm' (60-79) | 'cold' (<60)
            - score_breakdown: dict of each rubric component and points awarded
            - reasoning: 1-2 sentence explanation
            - recommended_action: 'immediate_outreach' | 'standard_queue' | 'nurture'
            - priority: int 1-5 (1=highest)
            """,
            agent=self.agent,
            expected_output="JSON with score, tier, reasoning, action, priority",
        )

        crew = Crew(agents=[self.agent], tasks=[task], verbose=False)
        result = crew.kickoff()

        # Parse score from result for logging
        scored = {**enriched_lead, "qualification": str(result)}
        logger.info(f"Lead qualified: {enriched_lead.get('name')}")
        return scored


if __name__ == "__main__":
    import json

    sample = {
        "name": "Sarah Johnson",
        "phone": "817-555-0199",
        "email": "sarah@example.com",
        "address": "456 Maple Ave, Fort Worth TX 76102",
        "property_type": "residential",
        "urgency": "emergency",
        "estimated_job_size": "large",
        "pain_points": ["storm damage", "active leak", "water in ceiling"],
    }

    agent = QualifierAgent()
    result = agent.score_lead(sample)
    print(json.dumps(result, indent=2, default=str))
