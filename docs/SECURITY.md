# Security

The only required credential is the built-in `GITHUB_TOKEN`. Workflows request `contents: read` and `issues: read` only. Tokens are supplied through the Actions environment and never printed. Logs contain stage, ticket ID, status, and latency, not Issue bodies, credentials, payment details, or unnecessary personal data. Network failures, malformed JSON, HTTP errors, timeouts, and rate limits produce safe error messages. Write methods require explicit enablement and human approval.
