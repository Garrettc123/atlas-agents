"""
ATLAS Agents — Entry Point
Runs a sample lead through the full Prospector → Qualifier → Outreach pipeline.
"""

import os
import json
from dotenv import load_dotenv
from agents import ProspectorAgent, QualifierAgent, OutreachAgent

load_dotenv()


def process_lead(raw_lead: dict, client_name: str = "DFW Roofing Pro") -> dict:
    """
    Full 3-agent pipeline: enrich → score → message.
    Returns complete lead record with all agent outputs.
    """
    print(f"\n{'='*60}")
    print(f"ATLAS Pipeline — Processing: {raw_lead.get('name')}")
    print('='*60)

    # Stage 1: Enrich
    print("[1/3] Prospector Agent enriching lead...")
    prospector = ProspectorAgent()
    enriched = prospector.enrich_lead(raw_lead)
    print("      ✓ Enrichment complete")

    # Stage 2: Score
    print("[2/3] Qualifier Agent scoring lead...")
    qualifier = QualifierAgent()
    scored = qualifier.score_lead(enriched)
    print("      ✓ Qualification complete")

    # Stage 3: Outreach
    print("[3/3] Outreach Agent generating messages...")
    outreach = OutreachAgent()
    sms = outreach.generate_outreach(scored, channel='sms', client_name=client_name)
    email = outreach.generate_outreach(scored, channel='email', client_name=client_name)
    print("      ✓ Outreach messages ready")

    result = {
        "raw": raw_lead,
        "enriched": enriched,
        "scored": scored,
        "sms_outreach": sms,
        "email_outreach": email,
    }

    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    return result


if __name__ == "__main__":
    test_lead = {
        "id": "test_001",
        "name": "John Martinez",
        "email": "john.martinez@example.com",
        "phone": "214-555-0123",
        "address": "1234 Oak St, Dallas TX 75201",
        "message": "Roof storm damage last night — water leaking into master bedroom. Need help ASAP.",
        "source": "website_form",
    }

    result = process_lead(test_lead, client_name="DFW Roofing Pro")
    print(json.dumps(result, indent=2, default=str))
