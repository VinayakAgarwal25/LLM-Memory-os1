# Memory OS

Memory OS is a modular long-term memory layer for AI assistants. It captures durable user information from conversation, stores it as structured memory, retrieves only the most relevant context at inference time, and keeps that memory base stable across long conversations and restarts.

This project is built around a simple idea: instead of replaying the entire chat history, let the assistant maintain a compact, evolving memory system with extraction, scoring, retrieval, reinforcement, decay, and archival.

## Why This Exists

LLMs are strong at local reasoning, but they often lose important user context in long conversations. Memory OS is designed to address that by:

- extracting durable user facts, preferences, and constraints,
- storing them in a structured persistent memory store,
- retrieving a small, high-signal subset when needed,
- keeping memory quality under control with confidence gating, deduplication, conflict handling, and decay.

## What It Does

- Hybrid retrieval using FAISS semantic search plus cognitive scoring.
- Structured memory objects with `type`, `key`, `value`, `source_turn`, `confidence`, and importance.
- Durable storage across sessions with JSON persistence and FAISS vector indexing.
- Memory upsert pipeline with duplicate merging and conflict resolution.
- Memory lifecycle controls including reinforcement, decay, expiry, and archival.
- Explainability tools through retrieval traces, stats, and analytics logs.
- Evaluation scripts for long-range recall, latency, stability, and hallucination-avoidance proxies.

## How It Works

For each user turn, Memory OS runs this loop:

1. Retrieve relevant memories for the current query using vector search and a weighted scoring pipeline.
2. Inject those memories into the generation prompt.
3. Generate the assistant response with Ollama.
4. Extract candidate memories from the interaction.
5. Score candidates for durability and importance.
6. Store, merge, discard, or resolve conflicts as needed.
7. Reinforce accessed memories and apply aging/archival policies.

The retrieval layer combines:

- semantic similarity from FAISS,
- importance weighting,
- freshness and decay bias,
- tier bonuses for short-term vs long-term memory,
- lexical overlap as a relevance gate,
- candidate pruning for scalability.

## Architecture

The repo is organized as a modular pipeline:

- `Configuration/`: runtime settings, thresholds, and dependency definitions.
- `LLM Interface/llm/`: Ollama client for generation and embeddings.
- `Storage Layer/storage/`: structured memory models, persistent storage, and FAISS vector search.
- `Memory System/memory/`: extraction, scoring, retrieval, aging, compression, injection, and cache logic.
- `Main Application/`: interactive chat loop, orchestration, analytics, and quickstart entrypoints.
- `Experiments/experiments/`: benchmark and evaluation scripts.
- `Demo Tools/`: simulator and visualization utilities.
- `docs/`: architecture, experiment notes, and demo flow.
- `submission/`: hackathon-facing summary material and final artifacts.

## Tech Stack

- Python
- Ollama for local LLM inference and embeddings
- `llama3.1:8b` for response generation
- `nomic-embed-text` for embeddings
- FAISS for vector similarity search

## Setup

Prerequisites:

- Python 3.8+
- Ollama running locally at `http://localhost:11434`
- The required models pulled in Ollama

Install dependencies:

```powershell
python -m pip install -r "Configuration/requirements.txt"
```

Pull the models if needed:

```powershell
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Start Ollama:

```powershell
ollama serve
```

Run the app:

```powershell
python "Main Application/main.py"
```

You can also use the guided launcher:

```powershell
python "Main Application/quickstart.py"
```

## Interactive Commands

Inside the chat interface:

- `stats`: show memory counts and cache stats
- `memories`: list stored memories
- `trace`: show retrieval scoring breakdown
- `analytics`: show reinforcement and storage analytics
- `integrity`: run integrity checks on stored memories
- `fresh`: clear retrieval cache for the next turn
- `reset`: wipe stored memories
- `quit`: save and exit

## Example Use Cases

- Personal AI assistants that should remember preferences across sessions
- Research copilots that need stable user context without replaying full transcripts
- Long-running conversational agents with explainable retrieval behavior
- Experimental memory systems for agent benchmarking and hackathon demos

## Evaluation

The repo includes scripts for:

- retrieval latency benchmarking,
- memory growth and scalability testing,
- cognitive stability validation,
- memory accuracy and recall checks,
- end-to-end hackathon-style evaluation at 200 and 1000 turns.

Run the bundled evaluation:

```powershell
python "Experiments/experiments/hackathon_evaluation.py" --turns 200 --out "Experiments/experiments/hackathon_report_200_final.json"
python "Experiments/experiments/hackathon_evaluation.py" --turns 1000 --out "Experiments/experiments/hackathon_report_1000_final.json"
```

Other benchmark scripts are documented in [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md).

## Included Results

Based on the checked-in evaluation reports in `Experiments/experiments/`:

- 200-turn evaluation: long-range recall `1.0`, retrieval relevance `1.0`, hallucination-avoidance proxy `1.0`
- 1000-turn evaluation: long-range recall `1.0`, retrieval relevance `1.0`, hallucination-avoidance proxy `1.0`
- Probe memories successfully retained across long runs:
  - preferred language: Kannada
  - call window: after 11 AM
  - diet: vegetarian

Latency varies between cold starts and steady-state runs, but the evaluation artifacts show near-real-time retrieval behavior in the benchmarked path.

## Notable Design Choices

- Durable memory focus: the extractor tries to keep temporary chatter out of long-term storage.
- Structured memory schema: retrieval and conflict handling operate on typed memory records, not raw transcript chunks.
- Explainability first: `trace` exposes retrieval decisions and score breakdowns.
- Stability controls: decay, archival, and confidence thresholds prevent unbounded memory growth.
- Local-first stack: the system runs with Ollama and does not depend on hosted APIs.

## Current Limitations

- The default pipeline is tuned around local Ollama models and local file persistence.
- Some memory extraction and importance scoring behavior is heuristic and model-dependent.
- Directory names contain spaces, so paths should be quoted when running scripts from the terminal.
- Compression exists in the codebase but is disabled by default in the current configuration.

## Repo Notes

- Persistent data lives under `Main Application/data/`.
- Default configuration is defined in `Configuration/config.py`.
- Architecture notes and demo flow are in `docs/ARCHITECTURE.md` and `docs/DEMO_FLOW.md`.

## Summary

Memory OS is a practical prototype for giving AI assistants a more durable, explainable memory system. It combines vector retrieval, structured storage, lifecycle management, and benchmark tooling in a modular local-first codebase that is easy to demo, extend, and evaluate.
