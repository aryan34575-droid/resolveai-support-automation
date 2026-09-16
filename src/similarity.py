from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List


def tokens(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) > 2}


def similar_issues(issue: Dict[str, Any], candidates: Iterable[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
    query = tokens(f"{issue.get('title', '')} {issue.get('body') or ''}")
    matches = []
    for candidate in candidates:
        if candidate.get("number") == issue.get("number"):
            continue
        score = len(query & tokens(f"{candidate.get('title', '')} {candidate.get('body') or ''}")) / max(len(query), 1)
        if score:
            matches.append({"issue_number": candidate.get("number"), "title": candidate.get("title", "Untitled issue"),
                            "score": round(score, 3), "source": "github_api"})
    return sorted(matches, key=lambda item: item["score"], reverse=True)[:limit]
