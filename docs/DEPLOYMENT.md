# Free GitHub deployment

1. Use the existing repository `aryan34575-droid/resolveai-support-automation`.
2. Push this project to its `main` branch.
3. Enable Actions in repository settings.
4. Confirm workflow permissions remain `contents: read` and `issues: read`.
5. Run **Actions -> ResolveAI manual test -> Run workflow**.
6. Download the completed `resolveai-manual-report` artifact.
7. Leave Actions enabled for the weekly scheduled workflow.

No paid hosting, paid API, paid SaaS, external model key, or credit card is required. GitHub Actions automatically exposes the repository token through `${{ secrets.GITHUB_TOKEN }}`; no manually entered token is required for workflow execution. If a run fails, verify permissions, confirm open Issues exist, and inspect the redacted API error in the failed step.

## GitHub Pages dashboard

The dashboard is available at:

https://aryan34575-droid.github.io/resolveai-support-automation/

The `dashboard.yml` workflow runs for manual dispatch, weekly schedule, and Issue opened/edited/reopened events. It uses `issues: read` to analyze Issues, `contents: write` only to persist the sanitized `docs/report.json`, and `pages: write` plus `id-token: write` to deploy the static site. Browser code only fetches the public `report.json`; it never receives or uses `GITHUB_TOKEN`.
