# Evaluation

`evaluate.py` runs the reproducible, labelled synthetic dataset and calculates category accuracy, priority accuracy, routing accuracy, duplicate detection rate, response groundedness, human-review rate, and mean latency. It prints measured values at runtime; no metrics are claimed here because they must come from an execution.

The three fixtures are synthetic and intentionally small. They test billing, account, and shipping paths plus retrieval. Unit tests cover the complete workflow, approval safety, malformed JSON, missing fields, and empty messages. Production evaluation should add a representative, privacy-reviewed, human-labelled holdout set and separately measure calibration, false escalation, false duplicate matches, and groundedness with human adjudication.
