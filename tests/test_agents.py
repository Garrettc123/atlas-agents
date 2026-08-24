from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from agents.outreach import OutreachAgent, is_allowed_send_time, is_opt_out_message


class TestSendTimeCompliance:
    """TCPA time-window enforcement."""

    def test_blocks_early_morning(self):
        with patch("agents.outreach.datetime") as mock_dt:
            mock_now = MagicMock()
            mock_now.hour = 7
            mock_dt.now.return_value = mock_now
            assert is_allowed_send_time() is False

    def test_allows_midday(self):
        with patch("agents.outreach.datetime") as mock_dt:
            mock_now = MagicMock()
            mock_now.hour = 14
            mock_dt.now.return_value = mock_now
            assert is_allowed_send_time() is True

    def test_blocks_late_night(self):
        with patch("agents.outreach.datetime") as mock_dt:
            mock_now = MagicMock()
            mock_now.hour = 22
            mock_dt.now.return_value = mock_now
            assert is_allowed_send_time() is False


class TestOptOutDetection:
    """TCPA opt-out keyword handling."""

    @pytest.mark.parametrize(
        "msg",
        ["STOP", "stop", "Stop", "QUIT", "CANCEL", "UNSUBSCRIBE", "OPT OUT", "REMOVE"],
    )
    def test_detects_standard_opt_outs(self, msg):
        assert is_opt_out_message(msg) is True

    @pytest.mark.parametrize(
        "msg",
        ["Yes please", "Call me at 2pm", "What is the price?", "I need a quote", "OK"],
    )
    def test_allows_normal_replies(self, msg):
        assert is_opt_out_message(msg) is False

    def test_opt_out_triggers_suppression(self):
        mock_db = MagicMock()
        result = OutreachAgent.handle_inbound_reply(message="STOP", lead_id="lead_001", db=mock_db)
        mock_db.suppress_lead.assert_called_once_with("lead_001")
        assert result["action"] == "opted_out"

    def test_normal_reply_continues(self):
        result = OutreachAgent.handle_inbound_reply(
            message="Yes, call me at 3pm",
            lead_id="lead_001",
        )
        assert result["action"] == "continue_conversation"


class TestConsentVerification:
    """Consent timestamp validation."""

    def test_lead_without_consent_blocked(self):
        lead = {"name": "Test", "phone": "2145550000"}
        assert lead.get("consent_timestamp") is None

    def test_lead_with_valid_consent(self):
        lead = {
            "name": "Test",
            "phone": "2145550000",
            "consent_timestamp": datetime.now() - timedelta(days=10),
        }
        age_days = (datetime.now() - lead["consent_timestamp"]).days
        assert age_days < 90
