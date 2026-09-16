import json
from src.resolveai.reporter import render_public_report, render_report


def test_report_generation():
    report = json.loads(render_report([{"ticket_id": "T1", "status": "awaiting_approval"}]))
    assert report["report_type"] == "analysis_only"
    assert report["results"][0]["ticket_id"] == "T1"


def test_public_report_excludes_ticket_content():
    report = json.loads(render_public_report([{
        "observed_ticket": {"issue_number": 7, "body": "private customer message"},
        "category": "technical",
        "priority": "high",
        "sentiment": "negative",
        "recommended_team": "Technical Support",
        "suggested_response": "AI-generated draft — human review required.",
        "confidence": 0.8,
        "human_review_required": True,
        "similar_tickets": [{"reference_id": "github-issue-2", "title": "private title", "score": 0.5}],
        "knowledge_references": [],
        "evidence": [],
    }]))
    assert report["summary"]["issues_analyzed"] == 1
    assert report["results"][0]["issue_label"] == "Issue #7"
    assert "private customer message" not in json.dumps(report)
    assert "private title" not in json.dumps(report)
