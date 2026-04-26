# Memory OS Modular Architecture

## Layers
- `LLM Interface`: generation + embeddings.
- `Storage Layer`: memory persistence, vector index, integrity checks.
- `Memory System`: extraction, scoring, retrieval, aging, compression, caching.
- `Main Application`: orchestration loop, chat commands, explainability, analytics.

## Retrieval Pipeline
1. Embed query.
2. FAISS preselect candidates (`VECTOR_CANDIDATE_K`).
3. Recency-window bounded filtering.
4. Tiered (short vs long-term) quota allocation.
5. Candidate hard-cap pruning.
6. Hybrid cognitive scoring.
7. LRU query cache insertion and explainable trace output.

## Quality Controls
- Hallucination guard on extraction.
- Confidence-threshold storage gating.
- Structured deduplication + conflict resolution.
- Memory integrity enforcement on load/save.
- Long-term stale archival policy.
