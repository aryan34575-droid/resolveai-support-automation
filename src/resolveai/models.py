from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

CATEGORIES = ("billing", "technical", "account", "product", "shipping", "security", "other")
PRIORITIES = ("low", "medium", "high", "urgent")
SENTIMENTS = ("positive", "neutral", "negative")


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    customer_message: str
    created_at: str
    product: str
    channel: str

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "Ticket":
        if not isinstance(value, dict):
            raise ValueError("ticket must be a JSON object")
        required = ("ticket_id", "customer_message", "created_at", "product", "channel")
        missing = [key for key in required if not isinstance(value.get(key), str) or not value[key].strip()]
        if missing:
            raise ValueError("missing or empty required fields: " + ", ".join(missing))
        from datetime import datetime
        try:
            datetime.fromisoformat(value["created_at"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("created_at must be ISO-8601") from exc
        return cls(*(value[key].strip() for key in required))


@dataclass(frozen=True)
class Evidence:
    statement: str
    source: str


@dataclass(frozen=True)
class Reference:
    reference_id: str
    title: str
    score: float
    source: str

    def __post_init__(self):
        if not self.reference_id or not self.title or not self.source:
            raise ValueError("reference fields must be non-empty")


@dataclass
class AnalysisResult:
    ticket_summary: str
    category: str
    priority: str
    sentiment: str
    recommended_team: str
    similar_tickets: List[Reference] = field(default_factory=list)
    knowledge_references: List[Reference] = field(default_factory=list)
    suggested_response: str = ""
    evidence: List[Evidence] = field(default_factory=list)
    confidence: float = 0.0
    human_review_required: bool = True
    review_reasons: List[str] = field(default_factory=list)
    observed_ticket: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
