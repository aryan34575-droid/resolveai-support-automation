from __future__ import annotations

from typing import List

from .models import Analysis, Reference, Ticket


def draft_response(ticket: Ticket, analysis: Analysis, articles: List[Reference]) -> str:
    if not articles:
        return "Thank you for contacting us. We have received your request and a team member will review it. We will follow up with next steps; this message does not indicate that the issue is resolved."
    names = ", ".join(article.title for article in articles[:2])
    return (f"Thank you for contacting us. We understand that you are contacting us about {analysis.category}. "
            f"Our {analysis.recommended_team} team will review the details. Relevant internal guidance: {names}. "
            "A team member must verify the guidance before sending it. This draft does not indicate that the issue is resolved.")
