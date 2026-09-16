from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from .adapters import KnowledgeBase, SimilarTicketStore, synthetic_stores
from .classifier import classify
from .logging_utils import StageLog, build_logger
from .models import Result, Ticket
from .response import draft_response

REQUIRED = ("ticket_id", "customer_message", "created_at")


class ResolveAI:
    def __init__(self, similar_store: Optional[SimilarTicketStore] = None, knowledge_base: Optional[KnowledgeBase] = None):
        default_similar, default_kb = synthetic_stores()
        self.similar_store, self.knowledge_base, self.logger = similar_store or default_similar, knowledge_base or default_kb, build_logger()

    def process(self, raw_ticket: Dict[str, Any], approved: bool = False) -> Result:
        observed = {key: value for key, value in raw_ticket.items() if key not in {"customer_name", "metadata"}} if isinstance(raw_ticket, dict) else {}
        ticket_id = str(raw_ticket.get("ticket_id", "unknown")) if isinstance(raw_ticket, dict) else "unknown"
        try:
            with StageLog(self.logger, ticket_id, "input_validation"):
                ticket = self._validate_and_normalize(raw_ticket)
            with StageLog(self.logger, ticket.ticket_id, "classification"):
                analysis = classify(ticket)
            with StageLog(self.logger, ticket.ticket_id, "similar_ticket_retrieval"):
                similar = self.similar_store.search(ticket)
            with StageLog(self.logger, ticket.ticket_id, "knowledge_retrieval"):
                articles = self.knowledge_base.search(ticket)
            with StageLog(self.logger, ticket.ticket_id, "response_generation"):
                response = draft_response(ticket, analysis, articles)
            result = Result(ticket.ticket_id, "awaiting_approval", observed, analysis, similar, articles, response, True)
            if approved and not analysis.human_review_required:
                result.status = "approved"
                result.update = {"customer_facing_response": response, "team": analysis.recommended_team, "safe_to_send": True}
            else:
                result.update = {"customer_facing_response": None, "team": analysis.recommended_team, "safe_to_send": False}
            return result
        except (ValueError, TypeError, KeyError) as exc:
            self.logger.error("validation failed", extra={"ticket_id": ticket_id, "stage": "input_validation", "success": False})
            return Result(ticket_id, "invalid", observed, errors=[str(exc)])
        except Exception as exc:
            self.logger.error("processing failed", extra={"ticket_id": ticket_id, "stage": "pipeline", "success": False})
            return Result(ticket_id, "failed", observed, errors=[f"processing failure: {exc}"])

    @staticmethod
    def _validate_and_normalize(raw: Dict[str, Any]) -> Ticket:
        if not isinstance(raw, dict):
            raise ValueError("ticket must be a JSON object")
        missing = [key for key in REQUIRED if not isinstance(raw.get(key), str) or not raw[key].strip()]
        if missing:
            raise ValueError(f"missing or empty required fields: {', '.join(missing)}")
        try:
            datetime.fromisoformat(raw["created_at"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("created_at must be ISO-8601") from exc
        return Ticket(raw["ticket_id"].strip(), " ".join(raw["customer_message"].split()), raw["created_at"].strip(),
                      raw.get("product"), raw.get("channel"), raw.get("customer_name"), raw.get("metadata", {}))


def process_json(raw_json: str, approved: bool = False) -> Dict[str, Any]:
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return Result("unknown", "invalid", {}, errors=[f"malformed JSON: {exc.msg}"]).to_dict()
    return ResolveAI().process(payload, approved=approved).to_dict()
