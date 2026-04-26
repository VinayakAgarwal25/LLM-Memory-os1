# Run Commands

## Setup
```powershell
cd memory-os
python -m pip install -r "Configuration/requirements.txt"
```

## Start System
```powershell
python "Main Application/main.py"
```

## Hackathon Evaluation
```powershell
python "Experiments/experiments/hackathon_evaluation.py" --turns 200 --out "Experiments/experiments/hackathon_report_200_final.json"
python "Experiments/experiments/hackathon_evaluation.py" --turns 1000 --out "Experiments/experiments/hackathon_report_1000_final.json"
```

## Optional Additional Experiments
```powershell
python "Experiments/experiments/retrieval_latency_benchmark.py"
python "Experiments/experiments/scalability_stress_test.py" --turns 1200
python "Experiments/experiments/latency_vs_memory_count.py"
python "Experiments/experiments/memory_accuracy_metrics.py"
python "Experiments/experiments/cognitive_stability_validation.py"
```
