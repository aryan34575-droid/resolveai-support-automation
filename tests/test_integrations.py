import pytest
from src.resolveai.github_client import GitHubAPIError, GitHubClient
from src.resolveai.pipeline import ResolveAI


def test_missing_github_token():
    with pytest.raises(GitHubAPIError, match="GITHUB_TOKEN"):
        GitHubClient(None, "owner/repo").list_issues()


def test_writes_require_explicit_approval():
    with pytest.raises(GitHubAPIError, match="human approval"):
        GitHubClient("token", "owner/repo").create_report_issue("title", "body", explicitly_enabled=True)


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
    client = GitHubClient("token", "owner/repo")
    monkeypatch.setattr("urllib.request.urlopen", broken)
    with pytest.raises(GitHubAPIError):
        client.list_issues()


def test_process_json_malformed_and_secret_not_in_observed():
    assert ResolveAI().process_json("{bad")["status"] == "invalid"
    data = ResolveAI().process_json('{"ticket_id":"T","customer_message":"help","created_at":"2026-01-01T00:00:00Z","product":"P","channel":"email","api_key":"secret"}')
    assert "api_key" not in data["analysis"]["observed_ticket"]
