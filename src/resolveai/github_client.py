from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


class GitHubAPIError(RuntimeError):
    """A safe, non-secret GitHub API failure."""


class GitHubClient:
    def __init__(self, token: str | None, repository: str | None, timeout: float = 20):
        self.token, self.repository, self.timeout = token, repository, timeout
        self.base_url = "https://api.github.com"

    def _request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
        if not self.token:
            raise GitHubAPIError("GITHUB_TOKEN is not configured")
        request = urllib.request.Request(self.base_url + path, method=method)
        request.add_header("Authorization", f"Bearer {self.token}")
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        if body is not None:
            request.add_header("Content-Type", "application/json")
            request.data = json.dumps(body).encode()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
                raise GitHubAPIError("GitHub API rate limit exceeded") from exc
            raise GitHubAPIError(f"GitHub API request failed: {type(exc).__name__}") from exc

    def _repo_path(self) -> str:
        if not self.repository or "/" not in self.repository:
            raise GitHubAPIError("GITHUB_REPOSITORY must be owner/name")
        return self.repository

    def list_issues(self, state: str = "open", limit: int = 30, since_days: int | None = None) -> List[Dict[str, Any]]:
        query = f"state={state}&sort=updated&direction=desc&per_page={min(limit, 100)}"
        if since_days is not None:
            since = datetime.now(timezone.utc) - timedelta(days=max(0, since_days))
            query += f"&since={since.isoformat().replace('+00:00', 'Z')}"
        data = self._request("GET", f"/repos/{self._repo_path()}/issues?{query}")
        return [item for item in data if "pull_request" not in item]

    @staticmethod
    def issue_to_ticket(issue: Dict[str, Any]) -> Dict[str, str]:
        if not isinstance(issue, dict) or not issue.get("number") or not issue.get("title"):
            raise GitHubAPIError("GitHub issue response missing number or title")
        body = issue.get("body") or ""
        return {
            "ticket_id": f"github-issue-{issue['number']}",
            "customer_message": f"{issue['title']}\n{body}".strip(),
            "created_at": issue.get("created_at", ""),
            "product": "GitHub Issues",
            "channel": "github",
        }

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) > 2}

    def similar_issue_references(self, issue: Dict[str, Any], issues: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
        query = self._tokens(f"{issue.get('title', '')} {issue.get('body') or ''}")
        candidates = []
        for candidate in issues:
            if candidate.get("number") == issue.get("number"):
                continue
            text = f"{candidate.get('title', '')} {candidate.get('body') or ''}"
            score = len(query & self._tokens(text)) / max(len(query), 1)
            if score:
                candidates.append({"reference_id": f"github-issue-{candidate['number']}",
                                   "title": candidate.get("title", "Untitled issue"),
                                   "score": round(score, 3), "source": "github_api"})
        return sorted(candidates, key=lambda item: item["score"], reverse=True)[:limit]

    def get_issue_comments(self, issue_number: int) -> List[Dict[str, Any]]:
        return self._request("GET", f"/repos/{self._repo_path()}/issues/{issue_number}/comments")

    def list_pull_requests(self, state: str = "open", limit: int = 30) -> List[Dict[str, Any]]:
        return self._request("GET", f"/repos/{self._repo_path()}/pulls?state={state}&per_page={min(limit, 100)}")

    def create_report_issue(self, title: str, body: str, explicitly_enabled: bool = False, approved: bool = False) -> Dict[str, Any]:
        if not explicitly_enabled or not approved:
            raise GitHubAPIError("write operation disabled; explicit enablement and human approval are required")
        return self._request("POST", f"/repos/{self._repo_path()}/issues", {"title": title, "body": body})

    def add_issue_comment(self, issue_number: int, body: str, explicitly_enabled: bool = False, approved: bool = False) -> Dict[str, Any]:
        if not explicitly_enabled or not approved:
            raise GitHubAPIError("write operation disabled; explicit enablement and human approval are required")
        return self._request("POST", f"/repos/{self._repo_path()}/issues/{issue_number}/comments", {"body": body})
