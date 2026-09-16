from src.similarity import similar_issues


def test_similarity_uses_local_token_overlap():
    issue = {"number": 1, "title": "Password reset error", "body": "account login fails"}
    candidates = [
        issue,
        {"number": 2, "title": "Login password reset", "body": "account access error"},
        {"number": 3, "title": "Package tracking", "body": "delivery delayed"},
    ]
    matches = similar_issues(issue, candidates)
    assert matches[0]["issue_number"] == 2
    assert matches[0]["source"] == "github_api"
