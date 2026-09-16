from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Protocol

from .models import Reference, Ticket


class SimilarTicketStore(Protocol):
    def search(self, ticket: Ticket, limit: int = 3) -> List[Reference]: ...


class KnowledgeBase(Protocol):
    def search(self, ticket: Ticket, limit: int = 3) -> List[Reference]: ...


def _tokens(text: str) -> set[str]:
    return {word.lower() for word in re.findall(r"[a-z0-9]+", text) if len(word) > 2}


@dataclass
class InMemoryReferenceStore:
    records: Iterable[Reference]
    texts: dict[str, str]

    def search(self, ticket: Ticket, limit: int = 3) -> List[Reference]:
        query = _tokens(ticket.customer_message)
        scored = []
        for record in self.records:
            score = len(query & _tokens(self.texts.get(record.reference_id, ""))) / max(len(query), 1)
            if score > 0:
                scored.append(Reference(record.reference_id, record.title, round(score, 3), record.source))
        return sorted(scored, key=lambda item: item.score, reverse=True)[:limit]


def synthetic_stores() -> tuple[SimilarTicketStore, KnowledgeBase]:
    similar = [
        Reference("SYN-TICKET-001", "Synthetic: duplicate invoice charge", 0, "synthetic_dataset"),
        Reference("SYN-TICKET-002", "Synthetic: password reset email missing", 0, "synthetic_dataset"),
        Reference("SYN-TICKET-003", "Synthetic: package delivery delayed", 0, "synthetic_dataset"),
    ]
    similar_texts = {
        "SYN-TICKET-001": "charged twice invoice duplicate payment billing",
        "SYN-TICKET-002": "password reset email account login access",
        "SYN-TICKET-003": "package delivery shipment delayed shipping",
    }
    articles = [
        Reference("SYN-KB-001", "Synthetic KB: duplicate charge investigation", 0, "synthetic_dataset"),
        Reference("SYN-KB-002", "Synthetic KB: account password reset", 0, "synthetic_dataset"),
        Reference("SYN-KB-003", "Synthetic KB: tracking and delayed delivery", 0, "synthetic_dataset"),
    ]
    article_texts = {
        "SYN-KB-001": "billing duplicate charged invoice payment",
        "SYN-KB-002": "account password reset login access",
        "SYN-KB-003": "shipping tracking package delivery delayed",
    }
    return InMemoryReferenceStore(similar, similar_texts), InMemoryReferenceStore(articles, article_texts)
