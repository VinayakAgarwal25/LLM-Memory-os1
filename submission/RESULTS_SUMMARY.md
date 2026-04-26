# Results Summary

## Primary Evaluation (Hackathon-Aligned)

### 200-turn report
Source: `memory-os/Experiments/experiments/hackathon_report_200_final.json`
- Long-range recall score: `1.0`
- Accuracy proxy (1..N): `1.0`
- Retrieval relevance: `1.0`
- Hallucination avoidance: `1.0`
- Latency: `p50=0.09ms`, `p95=1964.74ms`, `mean=105.04ms`
- Cognitive stability: `active=4`, `short_term=0`, `long_term=4`, `archived=0`

### 1000-turn report
Source: `memory-os/Experiments/experiments/hackathon_report_1000_final.json`
- Long-range recall score: `1.0`
- Accuracy proxy (1..N): `1.0`
- Retrieval relevance: `1.0`
- Hallucination avoidance: `1.0`
- Latency: `p50=0.09ms`, `p95=0.2ms`, `mean=21.11ms`
- Cognitive stability: `active=4`, `short_term=0`, `long_term=4`, `archived=0`

## Notes on Latency
- p95 spikes in shorter runs come from cold embedding/model calls.
- In steady-state repeated-query runtime, retrieval is near real-time (sub-ms p50 in this benchmark path).

## Probe Validation
In both 200 and 1000 runs, probes successfully recalled:
- Preferred language: Kannada
- Call window: after 11 AM
- Diet: vegetarian
