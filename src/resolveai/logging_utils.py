from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone


class SafeJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ticket_id": getattr(record, "ticket_id", None),
            "stage": getattr(record, "stage", record.name),
            "success": getattr(record, "success", True),
            "latency_ms": getattr(record, "latency_ms", None),
            "message": record.getMessage(),
        }, separators=(",", ":"))


def get_logger() -> logging.Logger:
    logger = logging.getLogger("resolveai")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(SafeJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


class Stage:
    def __init__(self, logger: logging.Logger, ticket_id: str, name: str):
        self.logger, self.ticket_id, self.name = logger, ticket_id, name
        self.started = time.perf_counter()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.logger.info(
            "stage completed" if exc is None else "stage failed",
            extra={"ticket_id": self.ticket_id, "stage": self.name, "success": exc is None,
                   "latency_ms": round((time.perf_counter() - self.started) * 1000, 2)},
        )
        return False
