# ResolveAI

ResolveAI is an independent AI Automation Engineering portfolio project. Synthetic data is used for testing. No real customer data, company deployment or production business impact is claimed. The project is not affiliated with or endorsed by any company.

## Problem and solution

Support teams need consistent triage, priority detection, duplicate detection, routing, and response drafting. ResolveAI reads GitHub Issues and produces a structured, evidence-based report without sending messages or making destructive changes.

## Architecture and workflow

`GitHub Issue -> extract fields -> validate -> local NLP classification -> priority -> sentiment -> similar Issues -> team recommendation -> response draft -> human review -> optional report/comment`.

Raw GitHub data is kept separate from recommendations. If evidence is insufficient, the analyzer reports `Insufficient evidence.` and requires human review.

## Features

- Reads Issue number, title, body, labels, creation date, and URL
- Classifies billing, technical, account, product, shipping, security, and other
- Detects low, medium, high, and urgent priority
- Detects positive, neutral, and negative sentiment
- Recommends Billing, Technical Support, Account Support, Product, Security, or Operations
- Finds similar Issues with local token-overlap scoring
- Produces `AI-generated draft — human review required.`
- Generates JSON reports without external side effects

## Tech stack and free-first design

Python standard library, JSON, GitHub REST API, the built-in `GITHUB_TOKEN`, and GitHub Actions. No paid service, external AI API, API key, SaaS account, hosting, or credit card is required. All classification and drafting logic runs locally and deterministically.

## Setup and testing

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m compileall .
python -m pytest -q
```

`test_data/synthetic_tickets.json` is clearly labelled synthetic and is never presented as company data. GitHub Actions receives the automatic repository-provided `${{ secrets.GITHUB_TOKEN }}`; no manually entered token or repository secret configuration is needed for Actions. Local GitHub API execution requires authentication supplied by the local environment; this is not needed in GitHub Actions.

## GitHub Actions and permissions

`manual-test.yml` runs compile, tests, and live open-Issue analysis on demand. `scheduled-audit.yml` runs weekly and analyzes recent/open Issues. Both use only the automatic `GITHUB_TOKEN` and request `contents: read` and `issues: read`. No repository secret is required.

Run **Actions -> ResolveAI manual test -> Run workflow**, then download the JSON artifact. Leave Actions enabled for weekly execution. See `docs/DEPLOYMENT.md`.

## Exact GitHub deployment steps

This repository already exists at `aryan34575-droid/resolveai-support-automation`. From an authenticated computer with GitHub CLI installed, update that repository with:

```powershell
gh auth login
git remote set-url origin https://github.com/aryan34575-droid/resolveai-support-automation.git
git push origin main
```

If `origin` is not configured:

```powershell
git remote add origin https://github.com/aryan34575-droid/resolveai-support-automation.git
git push -u origin main
```

Then enable Actions, confirm `contents: read` and `issues: read` under repository workflow permissions, run **Actions -> ResolveAI manual test -> Run workflow**, and download `resolveai-manual-report`. Verify the report contains Issue observations and separate recommendations. Leave Actions enabled and verify the weekly scheduled run under the Actions tab.

## Security and limitations

The built-in token is never logged. Logs omit Issue bodies, payment details, passwords, API keys, and unnecessary personal information. API failures, malformed responses, timeouts, and rate limits are surfaced safely. Security, urgent, ambiguous, and low-confidence Issues require human review. No response is sent; Issues are not closed, deleted, merged, suspended, or modified.

The local analyzer and token-overlap retrieval are intentionally modest. Production use would require a privacy-reviewed labelled evaluation set, access controls, retention controls, monitoring, retries, and an operational human-review process. Zendesk, Intercom, Freshdesk, and Salesforce Service Cloud are future adapter targets, not implemented integrations.

## Transparency

This is an independent AI Automation Engineering portfolio project. Synthetic data is used for testing. No real customer data, company deployment or production business impact is claimed.
