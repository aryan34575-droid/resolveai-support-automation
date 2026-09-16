from __future__ import annotations

import argparse
import json
import os
import sys

from .github_client import GitHubClient, GitHubAPIError
from .models import Reference, Ticket
from .pipeline import ResolveAI
from .reporter import render_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze support tickets without external side effects")
    parser.add_argument("--input", help="JSON file; defaults to stdin")
    parser.add_argument("--approved", action="store_true", help="record explicit human approval for safe recommendations")
    parser.add_argument("--github-issues", action="store_true", help="analyze open GitHub Issues using GITHUB_TOKEN")
    parser.add_argument("--publish-report-issue", action="store_true", help="create a GitHub report Issue; requires explicit opt-in")
    args = parser.parse_args()
    engine = ResolveAI()
    if not args.github_issues:
        raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
        print(json.dumps(engine.process_json(raw, args.approved), indent=2))
        return 0
    client = GitHubClient(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPOSITORY"))
    try:
        issues = client.list_issues()
        results = []
        for issue in issues:
            ticket = Ticket.from_dict(client.issue_to_ticket(issue))
            similar = [Reference(**item) for item in client.similar_issue_references(issue, issues)]
            result = engine.process_ticket(ticket, similar_tickets=similar).to_dict()
            result["observed_ticket"].update({
                "issue_number": issue.get("number"),
                "title": issue.get("title"),
                "body": issue.get("body"),
                "labels": [label.get("name") for label in issue.get("labels", []) if isinstance(label, dict)],
                "url": issue.get("html_url"),
            })
            results.append(result)
        report = render_report(results)
        if args.publish_report_issue:
            client.create_report_issue("ResolveAI analysis report", report, explicitly_enabled=True, approved=args.approved)
        print(report)
    except GitHubAPIError as exc:
        print(json.dumps({"status": "github_api_error", "errors": [str(exc)]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
