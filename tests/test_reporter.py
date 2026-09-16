import json
from src.resolveai.reporter import render_report


def test_report_generation():
    report = json.loads(render_report([{"ticket_id": "T1", "status": "awaiting_approval"}]))
    assert report["report_type"] == "analysis_only"
    assert report["results"][0]["ticket_id"] == "T1"
