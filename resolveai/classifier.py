from __future__ import annotations

import re
from typing import List

from .models import Analysis, Evidence, Ticket

KEYWORDS = {
    "billing": {"bill", "billing", "charge", "charged", "invoice", "payment", "refund"},
    "technical": {"error", "bug", "crash", "broken", "failure", "not working", "timeout"},
    "account": {"password", "login", "log in", "account", "access", "reset"},
    "product": {"feature", "product", "integration", "configure", "how do i"},
    "shipping": {"ship", "shipping", "delivery", "package", "tracking", "arrive"},
    "security": {"hack", "breach", "stolen", "phishing", "unauthorized", "security"},
}
URGENT = {"breach", "hacked", "stolen", "unauthorized", "down", "outage", "immediately"}
HIGH = {"blocked", "cannot", "can't", "failed", "failure", "error", "charged twice"}
NEGATIVE = {"angry", "frustrated", "bad", "upset", "unacceptable", "broken", "failed"}
POSITIVE = {"thanks", "great", "happy", "appreciate", "good"}
TEAM = {"billing": "Billing", "technical": "Technical Support", "account": "Account Support",
        "product": "Product Support", "shipping": "Logistics", "security": "Security",
        "other": "Customer Support"}


def _has(text: str, phrase: str) -> bool:
    return phrase in text if " " in phrase or "'" in phrase else bool(re.search(rf"\b{re.escape(phrase)}\b", text))


def classify(ticket: Ticket) -> Analysis:
    text = ticket.customer_message.lower()
    scores = {category: sum(_has(text, word) for word in words) for category, words in KEYWORDS.items()}
    category = max(scores, key=scores.get)
    if scores[category] == 0:
        category = "other"
    urgent = any(_has(text, word) for word in URGENT)
    high = any(_has(text, word) for word in HIGH)
    priority = "urgent" if urgent else "high" if high else "low"
    sentiment = "negative" if any(_has(text, word) for word in NEGATIVE) else "positive" if any(_has(text, word) for word in POSITIVE) else "neutral"
    evidence: List[Evidence] = [Evidence(f"matched term '{word}'", "observed customer_message")
                                for word in KEYWORDS.get(category, set()) if _has(text, word)]
    if urgent:
        evidence.append(Evidence("urgent-risk language detected", "observed customer_message"))
    confidence = min(0.98, 0.55 + 0.1 * min(len(evidence), 4)) if scores.get(category, 0) else 0.35
    reasons = []
    if category == "other" or confidence < 0.65:
        reasons.append("classification evidence is limited or ambiguous")
    if category == "security" or priority == "urgent":
        reasons.append("high-risk ticket requires human review")
    summary = re.sub(r"\s+", " ", ticket.customer_message).strip()
    summary = summary[:240] + ("..." if len(summary) > 240 else "")
    return Analysis(summary, category, priority, sentiment, TEAM[category], evidence, round(confidence, 2), bool(reasons), reasons)
