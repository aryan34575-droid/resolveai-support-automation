# Security

- Secrets are not hard-coded. Future API connectors must read credentials from environment variables or a managed secret store.
- Logs contain no message bodies, names, passwords, API keys, payment details, or unnecessary personal information.
- Adapter credentials should be read-only and scoped to ticket search/knowledge retrieval; separate credentials should be used for any future update API.
- Customer-facing responses require human approval. The baseline has no financial, destructive, account, or outbound-action capability.
- Validate payloads at the boundary, use timeouts/retries in production adapters, redact provider errors, and enforce authentication, authorization, rate limits, encryption, retention, and audit logging around deployed APIs.
- Synthetic data in `synthetic_tickets.json` and synthetic references are development-only and clearly labelled.
