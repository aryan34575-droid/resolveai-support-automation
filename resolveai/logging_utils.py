from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ticket_id": getattr(record, "ticket_id", None),
            "processing_stage": getattr(record, "stage", record.name),
            "success": getattr(record, "success", True),
            "latency_ms": getattr(record, "latency_ms", None),
            "message": record.getMessage(),
        }
        return json.dumps(payload, separators=(",", ":"))


def build_logger() -> logging.Logger:
    logger = logging.getLogger("resolveai")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


class StageLog:
    def __init__(self, logger: logging.Logger, ticket_id: str, stage: str):
        self.logger, self.ticket_id, self.stage = logger, ticket_id, stage
        self.started = time.perf_counter()

    def __enter__(self) -> "StageLog":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.logger.info(
            "stage completed" if exc is None else "stage failed",
            extra={
                "ticket_id": self.ticket_id,
                "stage": self.stage,
                "success": exc is None,
                "latency_ms": round((time.perf_counter() - self.started) * 1000, 2),
            },
        )
        return False
