# Free GitHub deployment

1. Create a repository named `resolveai-support-automation` with description: `Free-first AI support-ticket automation system for GitHub Issues with local NLP classification, triage, routing and human approval.`
2. Push this project to the repository's default branch.
3. Enable Actions in repository settings.
4. Confirm workflow permissions remain `contents: read` and `issues: read`.
5. Run **Actions -> ResolveAI manual test -> Run workflow**.
6. Download the completed `resolveai-manual-report` artifact.
7. Leave Actions enabled for the weekly scheduled workflow.

No paid hosting, paid API, paid SaaS, OpenAI key, or credit card is required. The built-in `GITHUB_TOKEN` is automatic. If a run fails, verify permissions, confirm open Issues exist, and inspect the redacted API error in the failed step.
