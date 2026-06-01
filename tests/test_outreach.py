"""TCPA compliance tests — must pass on every deploy."""
import pytest
from agents.outreach import OutreachAgent
from datetime import datetime, time


@pytest.fixture
def agent():
    return OutreachAgent()


def test_opt_out_detection(agent):
    assert agent.detect_opt_out("STOP") is True
    assert agent.detect_opt_out("stop please") is True
    assert agent.detect_opt_out("unsubscribe") is True
    assert agent.detect_opt_out("yes I am interested") is False


def test_opt_out_blocks_send(agent):
    agent.opt_out_list.add("2145550001")
    import asyncio
    result = asyncio.run(agent.send("+12145550001", "Hello!"))
    assert result["status"] == "blocked"
    assert result["reason"] == "opted_out"


def test_handle_reply_adds_to_opt_out(agent):
    result = agent.handle_reply("+12145550002", "stop")
    assert result == "opted_out"
    assert "2145550002" in agent.opt_out_list


def test_send_window_enforcement(agent):
    in_window = datetime(2026, 6, 1, 10, 0)   # 10 AM
    out_window = datetime(2026, 6, 1, 22, 0)  # 10 PM
    assert agent.is_send_window(in_window) is True
    assert agent.is_send_window(out_window) is False
