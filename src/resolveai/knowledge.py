from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Protocol

from .models import Reference, Ticket


class ReferenceStore(Protocol):
    def search(self, ticket: Ticket, limit: int = 3) -> List[Reference]: ...


@dataclass
class SyntheticReferenceStore:
    references: Iterable[Reference]
    text_by_id: dict[str, str]

    def search(self, ticket: Ticket, limit: int = 3) -> List[Reference]:
        query = set(re.findall(r"[a-z0-9]+", ticket.customer_message.lower()))
        matches = []
        for item in self.references:
            words = set(re.findall(r"[a-z0-9]+", self.text_by_id.get(item.reference_id, "").lower()))
            score = len(query & words) / max(len(query), 1)
            if score:
                matches.append(Reference(item.reference_id, item.title, round(score, 3), item.source))
        return sorted(matches, key=lambda x: x.score, reverse=True)[:limit]


def synthetic_stores() -> tuple[ReferenceStore, ReferenceStore]:
    tickets = [Reference("SYN-TICKET-001", "Synthetic duplicate invoice charge", 0, "synthetic_test_data"),
               Reference("SYN-TICKET-002", "Synthetic password reset email missing", 0, "synthetic_test_data"),
               Reference("SYN-TICKET-003", "Synthetic package delivery delayed", 0, "synthetic_test_data")]
    articles = [Reference("SYN-KB-001", "Synthetic KB duplicate charge guidance", 0, "synthetic_test_data"),
                Reference("SYN-KB-002", "Synthetic KB password reset guidance", 0, "synthetic_test_data"),
                Reference("SYN-KB-003", "Synthetic KB delayed delivery guidance", 0, "synthetic_test_data")]
    text = {"SYN-TICKET-001": "charged twice invoice duplicate billing payment", "SYN-TICKET-002": "password reset email login account", "SYN-TICKET-003": "package delivery tracking shipping delayed",
            "SYN-KB-001": "charged twice invoice duplicate billing payment", "SYN-KB-002": "password reset email login account", "SYN-KB-003": "package delivery tracking shipping delayed"}
    return SyntheticReferenceStore(tickets, text), SyntheticReferenceStore(articles, text)
