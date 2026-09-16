from __future__ import annotations

from typing import Any, Dict, Optional

from .knowledge import ReferenceStore, synthetic_stores
from .logging_utils import Stage, get_logger
from .models import AnalysisResult, Ticket
from .reporter import render_report
from .ticket_analyzer import LocalTicketAnalyzer


class ResolveAI:
    def __init__(self, analyzer=None, similar_store: Optional[ReferenceStore] = None, knowledge_store: Optional[ReferenceStore] = None):
        default_similar, default_knowledge = synthetic_stores()
        self.analyzer = analyzer or LocalTicketAnalyzer()
        self.similar_store = similar_store or default_similar
        self.knowledge_store = knowledge_store or default_knowledge
        self.logger = get_logger()

    def process(self, raw_ticket: Dict[str, Any], approved: bool = False) -> AnalysisResult:
        ticket_id = raw_ticket.get("ticket_id", "unknown") if isinstance(raw_ticket, dict) else "unknown"
        with Stage(self.logger, str(ticket_id), "validation"):
            ticket = Ticket.from_dict(raw_ticket)
        with Stage(self.logger, ticket.ticket_id, "ai_classification"):
            values = self.analyzer.analyze(ticket)
        with Stage(self.logger, ticket.ticket_id, "similar_ticket_detection"):
            similar = self.similar_store.search(ticket)
        with Stage(self.logger, ticket.ticket_id, "knowledge_retrieval"):
            knowledge = self.knowledge_store.search(ticket)
        response = ("AI-generated draft — human review required.\n"
                    "Thank you for contacting us. We received your request about " + str(values["category"]) +
                    ". A team member will review it and follow up with next steps; this draft does not indicate resolution.")
        result = AnalysisResult(**values, similar_tickets=similar, knowledge_references=knowledge,
                                suggested_response=response, observed_ticket={
                                    "ticket_id": ticket.ticket_id, "customer_message": ticket.customer_message,
                                    "created_at": ticket.created_at, "product": ticket.product, "channel": ticket.channel})
        if approved and not result.human_review_required:
            result.review_reasons.append("approval recorded; external write still requires an explicitly enabled adapter")
        return result

    def process_ticket(self, ticket: Ticket, similar_tickets=None, knowledge_references=None) -> AnalysisResult:
        values = self.analyzer.analyze(ticket)
        response = ("Thank you for contacting us. We received your request about " + str(values["category"]) +
                    ". A team member will review it and follow up with next steps; this draft does not indicate resolution.")
        return AnalysisResult(**values, similar_tickets=similar_tickets or [], knowledge_references=knowledge_references or [],
                              suggested_response=response, observed_ticket={
                                  "ticket_id": ticket.ticket_id, "customer_message": ticket.customer_message,
                                  "created_at": ticket.created_at, "product": ticket.product, "channel": ticket.channel})

    def process_json(self, raw_json: str, approved: bool = False) -> Dict[str, Any]:
        import json
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            return {"status": "invalid", "errors": [f"malformed JSON: {exc.msg}"]}
        try:
            return {"status": "awaiting_approval", "analysis": self.process(data, approved).to_dict()}
        except (ValueError, TypeError) as exc:
            return {"status": "invalid", "errors": [str(exc)]}
