# Experiment Results and Reporting Guide

Run from repo root:

```powershell
python "Experiments/experiments/retrieval_latency_benchmark.py"
python "Experiments/experiments/scalability_stress_test.py" --turns 1200
python "Experiments/experiments/latency_vs_memory_count.py"
python "Experiments/experiments/memory_accuracy_metrics.py"
python "Experiments/experiments/cognitive_stability_validation.py"
```

## Report Template
- Environment: OS, Python version, model used.
- Dataset/Prompt setup.
- Key metrics:
  - Retrieval latency (p50, p95, mean).
  - Active memory growth vs turn count.
  - Accuracy and relevance score.
  - Stability under long conversations.
- Failure cases and mitigations.
