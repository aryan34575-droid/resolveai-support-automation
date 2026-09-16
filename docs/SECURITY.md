# Security

The only workflow credential is the built-in `GITHUB_TOKEN`. Workflows request `contents: read` and `issues: read` only. The token is supplied through the Actions environment and never printed. Logs contain stage, ticket ID, status, and latency, not Issue bodies, credentials, payment details, or unnecessary personal data. Network failures, malformed JSON, HTTP errors, timeouts, and rate limits produce safe error messages. The implementation exposes no GitHub write operation: it only reads Issues and produces report artifacts.
