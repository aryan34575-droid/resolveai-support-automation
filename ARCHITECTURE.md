# Architecture

ResolveAI is a synchronous orchestration service with explicit stage boundaries. `ResolveAI.process` validates and normalizes an untrusted JSON object, runs analysis, retrieves references, creates a draft, and returns a `Result`. Every result includes observed ticket fields separately from recommendations.

Adapters are dependency-injected through `SimilarTicketStore` and `KnowledgeBase` protocols. Their `search` methods can wrap a helpdesk search API, vector database, or knowledge system later. Failures are surfaced as a failed result rather than silently converted into fabricated references. The current reference store is only a clearly labelled synthetic development fixture.

The approval boundary is deliberate: processing defaults to `awaiting_approval`; only an explicit `approved=True` and a non-risky, sufficiently confident analysis produce a `safe_to_send` update. No connector is provided that sends, refunds, cancels, deletes, or changes accounts.
