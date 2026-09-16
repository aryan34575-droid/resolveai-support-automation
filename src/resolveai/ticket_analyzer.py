from __future__ import annotations

import re
from typing import Dict, List

from .models import AnalysisResult, Evidence, Ticket

KEYWORDS = {
    "billing": {"bill", "billing", "charge", "charged", "invoice", "payment"},
    "technical": {"error", "bug", "crash", "broken", "failure", "timeout", "button", "working", "respond", "functionality"},
    "account": {"password", "login", "account", "access", "reset"},
    "product": {"feature", "integration", "configure", "product"},
    "shipping": {"ship", "shipping", "delivery", "package", "tracking", "arrive"},
    "security": {"hack", "breach", "stolen", "phishing", "unauthorized", "security"},
}
TEAMS = {"billing": "Billing", "technical": "Technical Support", "account": "Account Support", "product": "Product", "shipping": "Operations", "security": "Security", "other": "Operations"}


def _has(text: str, word: str) -> bool:
    return word in text if " " in word else bool(re.search(rf"\b{re.escape(word)}\b", text))


class LocalTicketAnalyzer:
    def analyze(self, ticket: Ticket) -> Dict[str, object]:
        text = ticket.customer_message.lower()
        scores = {key: sum(_has(text, word) for word in words) for key, words in KEYWORDS.items()}
        category = max(scores, key=scores.get) if max(scores.values(), default=0) else "other"
        urgent = any(_has(text, word) for word in ("breach", "hacked", "stolen", "unauthorized", "outage", "down"))
        high = any(_has(text, word) for word in ("blocked", "cannot", "failed", "error", "charged twice", "not working", "does not respond"))
        priority = "urgent" if urgent else "high" if high else "medium" if category != "other" else "low"
        negative = any(_has(text, word) for word in ("angry", "frustrated", "bad", "upset", "broken", "failed"))
        positive = any(_has(text, word) for word in ("thanks", "great", "happy", "appreciate"))
        sentiment = "negative" if negative else "positive" if positive else "neutral"
        evidence: List[Evidence] = [Evidence(f"matched '{word}'", "observed ticket.customer_message") for word in KEYWORDS.get(category, ()) if _has(text, word)]
        confidence = round(min(0.98, 0.55 + min(len(evidence), 4) * 0.1), 2) if category != "other" else 0.35
        reasons = []
        if category == "other" or confidence < 0.65:
            evidence.append(Evidence("Insufficient evidence.", "observed ticket.customer_message"))
            reasons.append("limited or ambiguous classification evidence")
        if priority in ("high", "urgent") or category == "security":
            reasons.append("high-risk or security-sensitive issue")
        summary = re.sub(r"\s+", " ", ticket.customer_message).strip()[:240]
        return {"ticket_summary": summary, "category": category, "priority": priority, "sentiment": sentiment,
                "recommended_team": TEAMS[category], "evidence": evidence, "confidence": confidence,
                "human_review_required": bool(reasons), "review_reasons": reasons}
