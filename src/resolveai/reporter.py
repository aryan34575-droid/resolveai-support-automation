from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable


def render_report(results: Iterable[Dict[str, Any]]) -> str:
    return json.dumps({"tool": "ResolveAI", "report_type": "analysis_only", "results": list(results)}, indent=2)


def write_report(results: Iterable[Dict[str, Any]], path: str = "resolveai-report.json") -> Path:
    destination = Path(path)
    destination.write_text(render_report(results) + "\n", encoding="utf-8")
    return destination
