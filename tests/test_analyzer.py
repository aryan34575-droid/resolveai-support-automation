from src.resolveai.models import Ticket
from src.resolveai.ticket_analyzer import LocalTicketAnalyzer


def make(message):
    return Ticket("T1", message, "2026-01-01T00:00:00Z", "P", "email")


def test_classification_priority_and_routing():
    result = LocalTicketAnalyzer().analyze(make("I was charged twice for my invoice."))
    assert result["category"] == "billing"
    assert result["priority"] == "high"
    assert result["recommended_team"] == "Billing"
    assert result["human_review_required"] is True


def test_login_button_failure_routes_to_technical_review():
    result = LocalTicketAnalyzer().analyze(make("The login button is not working and does not respond."))
    assert result["category"] == "technical"
    assert result["priority"] == "high"
    assert result["recommended_team"] == "Technical Support"
    assert result["human_review_required"] is True


def test_low_confidence_escalates():
    result = LocalTicketAnalyzer().analyze(make("Something happened."))
    assert result["human_review_required"] is True
    assert any(item.statement == "Insufficient evidence." for item in result["evidence"])


def test_security_escalates():
    result = LocalTicketAnalyzer().analyze(make("There was an unauthorized security breach."))
    assert result["category"] == "security"
    assert result["human_review_required"] is True
