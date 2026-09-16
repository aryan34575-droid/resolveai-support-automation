from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable


def render_report(results: Iterable[Dict[str, Any]]) -> str:
    return json.dumps({"tool": "ResolveAI", "report_type": "analysis_only", "results": list(results)}, indent=2)


def render_public_report(results: Iterable[Dict[str, Any]]) -> str:
    """Render a dashboard-safe report without ticket bodies or customer data."""
    safe_results = []
    category_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {}
    sentiment_counts: Dict[str, int] = {}
    team_counts: Dict[str, int] = {}
    results = list(results)
    for result in results:
        observed = result.get("observed_ticket", {})
        issue_number = observed.get("issue_number")
        category = result.get("category", "other")
        priority = result.get("priority", "low")
        sentiment = result.get("sentiment", "neutral")
        team = result.get("recommended_team", "Operations")
        category_counts[category] = category_counts.get(category, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        team_counts[team] = team_counts.get(team, 0) + 1
        safe_results.append({
            "issue_number": issue_number,
            "issue_label": f"Issue #{issue_number}" if issue_number is not None else "Issue",
            "category": category,
            "priority": priority,
            "sentiment": sentiment,
            "recommended_team": team,
            "similar_tickets": [
                {"reference_id": item.get("reference_id"), "score": item.get("score")}
                for item in result.get("similar_tickets", [])
            ],
            "knowledge_references": [
                {"reference_id": item.get("reference_id"), "score": item.get("score")}
                for item in result.get("knowledge_references", [])
            ],
            "suggested_response": result.get("suggested_response", ""),
            "confidence": result.get("confidence", 0),
            "human_review_required": bool(result.get("human_review_required", True)),
            "review_reasons": result.get("review_reasons", []),
            "evidence": result.get("evidence", []),
        })
    from datetime import datetime, timezone
    report = {
        "tool": "ResolveAI",
        "report_type": "public_dashboard",
        "safety": "ResolveAI analysis — read-only",
        "last_analysis": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "issues_analyzed": len(safe_results),
            "high_or_urgent": sum(item["priority"] in ("high", "urgent") for item in safe_results),
            "human_review_required": sum(item["human_review_required"] for item in safe_results),
        },
        "distributions": {
            "categories": category_counts,
            "priorities": priority_counts,
            "sentiments": sentiment_counts,
            "teams": team_counts,
        },
        "results": safe_results,
    }
    return json.dumps(report, indent=2)


def write_report(results: Iterable[Dict[str, Any]], path: str = "resolveai-report.json") -> Path:
    destination = Path(path)
    destination.write_text(render_report(results) + "\n", encoding="utf-8")
    return destination
