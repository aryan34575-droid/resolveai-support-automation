from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    github_token: str | None
    github_repository: str | None
    openai_api_key: str | None
    openai_model: str
    publish_report: bool
    write_enabled: bool
    timeout_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            os.getenv("GITHUB_TOKEN"),
            os.getenv("GITHUB_REPOSITORY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            os.getenv("PUBLISH_REPORT", "false").lower() == "true",
            os.getenv("RESOLVEAI_WRITE_ENABLED", "false").lower() == "true",
            float(os.getenv("RESOLVEAI_TIMEOUT_SECONDS", "20")),
        )
