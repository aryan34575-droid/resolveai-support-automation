from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

CATEGORIES = {"billing", "technical", "account", "product", "shipping", "security", "other"}
PRIORITIES = {"low", "medium", "high", "urgent"}
SENTIMENTS = {"positive", "neutral", "negative"}


@dataclass
class Ticket:
    ticket_id: str
    customer_message: str
    created_at: str
    product: Optional[str] = None
    channel: Optional[str] = None
    customer_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Evidence:
    signal: str
    source: str


@dataclass
class Analysis:
    summary: str
    category: str
    priority: str
    sentiment: str
    recommended_team: str
    evidence: List[Evidence]
    confidence: float
    human_review_required: bool
    review_reasons: List[str] = field(default_factory=list)


@dataclass
class Reference:
    reference_id: str
    title: str
    score: float
    source: str


@dataclass
class Result:
    ticket_id: str
    status: str
    observed_ticket: Dict[str, Any]
    analysis: Optional[Analysis] = None
    similar_issues: List[Reference] = field(default_factory=list)
    knowledge_articles: List[Reference] = field(default_factory=list)
    suggested_response: Optional[str] = None
    approval_required: bool = True
    update: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
