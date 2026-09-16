import json
import time
from pathlib import Path
from src.resolveai.pipeline import ResolveAI

data = json.loads(Path("synthetic_tickets.json").read_text(encoding="utf-8"))
engine = ResolveAI()
counts = {"classification_accuracy": 0, "priority_accuracy": 0, "routing_accuracy": 0, "duplicate_detection_quality": 0, "groundedness": 0}
latencies = []
for ticket in data:
    started = time.perf_counter()
    result = engine.process(ticket)
    latencies.append((time.perf_counter() - started) * 1000)
    counts["classification_accuracy"] += result.category == ticket["expected_category"]
    counts["priority_accuracy"] += result.priority == ticket["expected_priority"]
    counts["routing_accuracy"] += result.recommended_team == ticket["expected_team"]
    counts["duplicate_detection_quality"] += bool(result.similar_tickets)
    counts["groundedness"] += all(ref.source == "synthetic_test_data" for ref in result.knowledge_references)
n = len(data)
print(json.dumps({"dataset": "SYNTHETIC TEST DATA only", "tickets": n,
                  **{key: round(value / n, 3) for key, value in counts.items()},
                  "escalation_rate": round(sum(engine.process(item).human_review_required for item in data) / n, 3),
                  "mean_processing_latency_ms": round(sum(latencies) / n, 2)}, indent=2))
