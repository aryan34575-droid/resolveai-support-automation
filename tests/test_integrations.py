import pytest

from src.resolveai.github_client import GitHubAPIError, GitHubClient
from src.resolveai.pipeline import ResolveAI


def test_tokenless_public_api_mode(monkeypatch):
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"[]"

    def request(url, **kwargs):
        captured["request"] = url
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", request)
    assert GitHubClient(None, "owner/repo").list_issues() == []
    assert "Authorization" not in captured["request"].headers


def test_github_issue_conversion_and_similar_references():
    client = GitHubClient("token", "owner/repo")
    issue = {"number": 1, "title": "Login error", "body": "password reset fails", "created_at": "2026-01-01T00:00:00Z"}
    other = {"number": 2, "title": "Password reset error", "body": "account login fails"}
    ticket = client.issue_to_ticket(issue)
    assert ticket["ticket_id"] == "github-issue-1"
    assert client.similar_issue_references(issue, [issue, other])[0]["reference_id"] == "github-issue-2"


def test_malformed_api_response(monkeypatch):
    import json

    def broken(*args, **kwargs):
        raise json.JSONDecodeError("bad", "", 0)

    monkeypatch.setattr("urllib.request.urlopen", broken)
    with pytest.raises(GitHubAPIError):
        GitHubClient("token", "owner/repo").list_issues()


def test_authenticated_actions_mode(monkeypatch):
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"[]"

    def request(url, **kwargs):
        captured["request"] = url
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", request)
    GitHubClient("secret-token", "owner/repo").list_issues()
    assert captured["request"].headers["Authorization"] == "Bearer secret-token"


def test_tokenless_write_is_rejected():
    with pytest.raises(GitHubAPIError, match="GET requests only"):
        GitHubClient(None, "owner/repo")._request("POST", "/repos/owner/repo/issues")


def test_rate_limit_error(monkeypatch):
    import urllib.error

    def limited(*args, **kwargs):
        raise urllib.error.HTTPError("https://api.github.com", 429, "rate limited", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", limited)
    with pytest.raises(GitHubAPIError, match="rate limit or access restriction"):
        GitHubClient(None, "owner/repo").list_issues()


def test_private_repository_404(monkeypatch):
    import urllib.error

    def missing(*args, **kwargs):
        raise urllib.error.HTTPError("https://api.github.com", 404, "not found", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", missing)
    with pytest.raises(GitHubAPIError, match="public repository"):
        GitHubClient(None, "owner/private").list_issues()


def test_process_json_malformed_and_secret_not_in_observed():
    assert ResolveAI().process_json("{bad")["status"] == "invalid"
    data = ResolveAI().process_json('{"ticket_id":"T","customer_message":"help","created_at":"2026-01-01T00:00:00Z","product":"P","channel":"email","api_key":"secret"}')
    assert "api_key" not in data["analysis"]["observed_ticket"]
