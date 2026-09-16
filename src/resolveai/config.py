from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    github_token: str | None
    github_repository: str | None
    timeout_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            os.getenv("GITHUB_TOKEN"),
            os.getenv("GITHUB_REPOSITORY"),
            float(os.getenv("RESOLVEAI_TIMEOUT_SECONDS", "20")),
        )
