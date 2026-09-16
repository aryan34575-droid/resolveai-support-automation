from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict


class OpenAIAPIError(RuntimeError):
    pass


class OpenAIAnalyzer:
    def __init__(self, api_key: str | None, model: str = "gpt-4o-mini", timeout: float = 20):
        self.api_key, self.model, self.timeout = api_key, model, timeout

    def analyze(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            raise OpenAIAPIError("OPENAI_API_KEY is not configured")
        payload = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Return JSON only. Never invent facts. Use only the allowed labels. Include evidence from the ticket."},
                {"role": "user", "content": json.dumps({"ticket": ticket, "allowed_categories": ["billing", "technical", "account", "product", "shipping", "security", "other"], "allowed_priorities": ["low", "medium", "high", "urgent"], "allowed_sentiments": ["positive", "neutral", "negative"]})},
            ],
        }
        request = urllib.request.Request("https://api.openai.com/v1/chat/completions", method="POST", data=json.dumps(payload).encode())
        request.add_header("Authorization", f"Bearer {self.api_key}")
        request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
            content = data["choices"][0]["message"]["content"]
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError("model response is not an object")
            return result
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
            raise OpenAIAPIError(f"OpenAI analysis failed: {type(exc).__name__}") from exc
