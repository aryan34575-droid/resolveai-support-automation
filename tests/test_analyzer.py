from src.resolveai.models import Ticket
from src.resolveai.ticket_analyzer import LocalTicketAnalyzer


def make(message):
    return Ticket("T1", message, "2026-01-01T00:00:00Z", "P", "email")


def test_classification_priority_and_routing():
    result = LocalTicketAnalyzer().analyze(make("I was charged twice for my invoice."))
    assert result["category"] == "billing"
    assert result["priority"] == "high"
    assert result["recommended_team"] == "Billing"


def test_low_confidence_escalates():
    assert LocalTicketAnalyzer().analyze(make("Something happened."))["human_review_required"] is True


def test_security_escalates():
    result = LocalTicketAnalyzer().analyze(make("There was an unauthorized security breach."))
    assert result["category"] == "security"
    assert result["human_review_required"] is True
