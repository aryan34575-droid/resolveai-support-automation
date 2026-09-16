import pytest
from src.resolveai.models import Ticket


def test_valid_ticket():
    ticket = Ticket.from_dict({"ticket_id": "T1", "customer_message": "Help", "created_at": "2026-01-01T00:00:00Z", "product": "P", "channel": "email"})
    assert ticket.ticket_id == "T1"


@pytest.mark.parametrize("value", [{}, None, {"ticket_id": "T1"}])
def test_missing_or_empty_ticket(value):
    with pytest.raises((ValueError, TypeError)):
        Ticket.from_dict(value)
