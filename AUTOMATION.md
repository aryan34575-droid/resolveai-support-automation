# Automation contract

1. **Input validation / normalization:** require non-empty ID, message, and ISO-8601 creation time; normalize whitespace.
2. **Classification:** assign one allowed category and preserve matched-message evidence.
3. **Priority and sentiment:** assign constrained labels from observed language.
4. **Similar retrieval:** return only adapter-provided references with scores.
5. **Knowledge retrieval:** return only adapter-provided article IDs/titles.
6. **Response generation:** cite retrieved article titles when available; otherwise use a non-committal acknowledgement.
7. **Routing:** map category to a recommended team.
8. **Human approval:** all customer-facing output is a draft; urgent, security, ambiguous, and low-confidence work remains gated.
9. **Final update:** the result contains a safe update proposal, never an automatic external side effect.

Malformed JSON, missing fields, empty messages, invalid dates, adapter errors, and unexpected processing failures return structured error results and JSON logs.
