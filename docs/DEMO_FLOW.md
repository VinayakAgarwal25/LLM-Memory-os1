# Hackathon Demo Script and Presentation Flow

## 1) Setup (30s)
- Start Ollama (`ollama serve`).
- Launch app: `python "Main Application/main.py"`.

## 2) Memory Capture (60s)
- Provide user profile facts and preferences.
- Ask unrelated questions to simulate noise.

## 3) Explainable Retrieval (45s)
- Run `trace` command.
- Show hybrid score breakdown and selected memories.

## 4) Quality Controls (45s)
- Show conflict update (change a preference).
- Show `analytics` and `stats`.
- Mention hallucination guard and confidence thresholds.

## 5) Scalability Proof (60s)
- Run stress benchmark script (`scalability_stress_test.py`).
- Show stable active memory counts with archival.

## 6) Close (30s)
- Highlight modular architecture + Docker/setup reproducibility.
