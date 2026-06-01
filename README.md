# ATLAS Agents 🤖

> **Autonomous Transaction & Lead Automation System**  
> CrewAI-powered multi-agent pipeline for contractor revenue automation  
> Built by [Garcar Enterprise](https://github.com/Garrettc123)

[![CI](https://github.com/Garrettc123/atlas-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/Garrettc123/atlas-agents/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![CrewAI](https://img.shields.io/badge/framework-CrewAI-orange.svg)](https://crewai.com)

---

## Overview

ATLAS Agents is the AI brain of the ATLAS platform. Seven specialized agents work in concert to handle the entire contractor sales cycle — from lead enrichment to revenue collection — without human intervention.

## Agent Roster

| Agent | Role | Key Output |
|-------|------|------------|
| 🔍 Prospector | Lead enrichment | Property type, urgency, job size |
| ⚖️ Qualifier | Lead scoring 0-100 | Hot/Warm/Cold tier + recommended action |
| 📧 Outreach | Personalized messaging | Custom SMS/Email per lead |
| 💬 Conversation | Dialogue management | Objection handling, rapport |
| 📅 Scheduler | Appointment booking | Calendar invite confirmed |
| 💰 Revenue | Quote + payment | Stripe payment link |
| 📊 Analytics | Performance tracking | Daily conversion reports |

## Architecture

```
raw_lead → Prospector → Qualifier → Outreach → Conversation → Scheduler → Revenue → Analytics
                            ↓
                      score < 60
                            ↓
                      Nurture Queue
```

## Quick Start

```bash
git clone https://github.com/Garrettc123/atlas-agents.git
cd atlas-agents
pip install -r requirements.txt
cp .env.example .env   # Fill in your API keys
python main.py
```

## Environment Variables

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
```

## Testing

```bash
pytest tests/ -v --cov=agents
```

## CI/CD

GitHub Actions automatically runs on every push:
- Linting (flake8 + black)
- Unit tests (pytest)
- Coverage reporting
- Deploy to Railway on `main`

## Pricing

| Tier | Price | Agents | Leads/mo |
|------|-------|--------|----------|
| Foundation | $299/mo | 1 | 100 |
| Professional | $597/mo | 7 | 500 |
| Enterprise | $997/mo | Unlimited | Unlimited |

---

© 2026 Garcar Enterprise — Alvarado, Texas
