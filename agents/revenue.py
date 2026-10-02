class RevenueAgent:
    """Quote generation and Stripe payment link."""
    def __init__(self):
        self.processed = 0
        self.name = "Revenue"

    def generate_quote(self, lead: dict, tier: str = "Professional") -> dict:
        prices = {"Foundation": 299, "Professional": 597, "Enterprise": 997}
        self.processed += 1
        return {
            **lead,
            "quote_tier": tier,
            "amount": prices.get(tier, 597),
            "stripe_payment_link": "https://buy.stripe.com/test_demo_link",
        }
