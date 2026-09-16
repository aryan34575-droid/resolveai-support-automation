# Architecture

`src/github_client.py` reads authenticated GitHub Issues and extracts number, title, body, labels, creation date, and URL. `src/ticket_analyzer.py` performs deterministic local NLP scoring. `src/similarity.py` calculates token overlap. `src/reporter.py` serializes raw GitHub evidence separately from recommendations. `src/main.py` orchestrates the analysis-only workflow.

The default execution graph is: Issue read -> extraction -> validation -> local NLP -> similarity -> routing -> draft -> JSON artifact. No external customer system is contacted. Optional model adapters can be added behind the analyzer interface later.
