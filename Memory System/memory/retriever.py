"""
Memory Retriever - Hybrid retrieval with explainable scoring.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import math
import time

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "Storage Layer" / "storage"))
sys.path.append(str(PROJECT_ROOT / "LLM Interface" / "llm"))
sys.path.append(str(PROJECT_ROOT / "Configuration"))

from models import Memory
from memory_store import MemoryStore
from client import LLMClient
from memory.cache import LRUCache
import config


class MemoryRetriever:
    def __init__(self, memory_store: MemoryStore, llm_client: LLMClient):
        self.store = memory_store
        self.llm = llm_client
        self.query_cache = LRUCache(config.RETRIEVAL_CACHE_SIZE)
        self.embedding_cache = LRUCache(256)
        self.last_trace: Dict = {}
        self.cache_hits = 0
        self.cache_misses = 0

        if getattr(config, "DEBUG", False):
            print("Memory retriever initialized")

    def retrieve(self, query: str, current_turn: int, k: int = None) -> List[Memory]:
        start_time = time.time()
        k = min(k or config.MAX_MEMORIES_TO_RETRIEVE, config.MAX_CONTEXT_MEMORIES)
        query_key = query.lower().strip()

        cached = self._get_cached_results(query_key, current_turn)
        if cached is not None:
            self.cache_hits += 1
            self.last_trace = cached["trace"]
            return cached["memories"]

        self.cache_misses += 1
        query_embedding = self.embedding_cache.get(query_key)
        if query_embedding is None:
            query_embedding = self.llm.embed(query)
            if query_embedding:
                self.embedding_cache.set(query_key, query_embedding)
        if not query_embedding:
            self.last_trace = {"query": query, "reason": "no-query-embedding"}
            return []

        vector_candidates = self.store.vector_store.search(
            query_embedding,
            k=config.VECTOR_CANDIDATE_K
        )
        vector_similarity = {mid: sim for mid, sim in vector_candidates}

        candidates = self._collect_candidates(current_turn, vector_similarity)
        if not candidates:
            self.last_trace = {"query": query, "reason": "no-valid-candidates"}
            return []

        pruned_candidates = self._prune_candidates(candidates)
        scored = []
        for memory in pruned_candidates:
            breakdown = self._score_breakdown(memory, query, query_embedding, vector_similarity)
            scored.append((memory, breakdown["total"], breakdown))

        scored = [item for item in scored if item[2]["relevance_gate"]]
        if not scored:
            self.last_trace = {
                "query": query,
                "turn": current_turn,
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "candidate_count": len(candidates),
                "scored_count": 0,
                "selected_count": 0,
                "reason": "all-candidates-below-semantic-threshold",
                "top": [],
            }
            return []

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:k]
        selected_memories = [m for m, _, _ in top]

        for memory in selected_memories:
            memory.access(current_turn)

        elapsed = time.time() - start_time
        self.last_trace = self._build_trace(query, current_turn, elapsed, scored, top, len(candidates))
        self._cache_results(query_key, current_turn, selected_memories, self.last_trace)
        return selected_memories

    def get_last_trace(self) -> Dict:
        return self.last_trace or {}

    def get_cache_stats(self) -> Dict:
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total) if total else 0.0
        return {
            "size": len(self.query_cache),
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": round(hit_rate, 3),
        }

    def _get_cached_results(self, query_key: str, current_turn: int) -> Optional[Dict]:
        if not config.ENABLE_RETRIEVAL_CACHE:
            return None

        entry = self.query_cache.get(query_key)
        if not entry:
            return None

        if current_turn - entry["turn"] > config.RETRIEVAL_CACHE_TTL_TURNS:
            return None

        memories = []
        for mid in entry["memory_ids"]:
            memory = self.store.get_memory(mid)
            if memory and not memory.is_expired():
                memories.append(memory)
        if not memories:
            return None

        return {"memories": memories, "trace": entry["trace"]}

    def _cache_results(self, query_key: str, current_turn: int, memories: List[Memory], trace: Dict):
        if not config.ENABLE_RETRIEVAL_CACHE:
            return
        self.query_cache.set(
            query_key,
            {
                "turn": current_turn,
                "memory_ids": [m.id for m in memories],
                "trace": trace,
            }
        )

    def _collect_candidates(self, current_turn: int, vector_similarity: Dict[str, float]) -> List[Memory]:
        all_memories = self.store.get_all_memories(include_archived=False)
        valid = []
        for memory in all_memories:
            if memory.is_expired():
                continue
            if memory.importance < config.MIN_IMPORTANCE_THRESHOLD:
                continue
            if not memory.embedding:
                continue
            age_turns = current_turn - memory.source_turn
            if memory.tier == "short_term" and age_turns > config.RECENCY_WINDOW_TURNS:
                continue
            # Keep memory if vector shortlist includes it OR it is cognitively strong.
            if memory.id in vector_similarity or memory.importance >= config.SHORT_TERM_THRESHOLD or memory.usage_count > 1:
                valid.append(memory)

        short_term = [m for m in valid if m.tier == "short_term"]
        long_term = [m for m in valid if m.tier == "long_term"]
        if len(valid) <= config.CANDIDATE_HARD_CAP:
            return valid

        total_budget = config.CANDIDATE_HARD_CAP
        st_target = int(total_budget * config.SHORT_TERM_RETRIEVAL_QUOTA)
        lt_target = int(total_budget * config.LONG_TERM_RETRIEVAL_QUOTA)

        short_sorted = sorted(short_term, key=lambda m: m.importance, reverse=True)
        long_sorted = sorted(long_term, key=lambda m: m.importance, reverse=True)

        selected = short_sorted[:st_target] + long_sorted[:lt_target]
        selected_ids = {m.id for m in selected}
        remainder = [m for m in sorted(valid, key=lambda m: m.importance, reverse=True) if m.id not in selected_ids]

        while len(selected) < total_budget and remainder:
            selected.append(remainder.pop(0))

        return selected[:total_budget]

    def _prune_candidates(self, candidates: List[Memory]) -> List[Memory]:
        if len(candidates) <= config.CANDIDATE_HARD_CAP:
            return candidates
        return sorted(
            candidates,
            key=lambda m: (m.importance, m.usage_count, m.last_used_turn or 0),
            reverse=True
        )[:config.CANDIDATE_HARD_CAP]

    def _score_breakdown(
        self,
        memory: Memory,
        query_text: str,
        query_embedding: List[float],
        vector_similarity: Dict[str, float]
    ) -> Dict[str, float]:
        semantic = vector_similarity.get(memory.id)
        if semantic is None:
            semantic = self._cosine_similarity(memory.embedding, query_embedding)

        importance = memory.importance
        freshness = self._compute_freshness(memory)
        decay_bias = self._decay_bias(memory)
        tier_bonus = 0.0
        if semantic >= config.MIN_SEMANTIC_RELEVANCE:
            tier_bonus = config.LONG_TERM_TIER_BONUS if memory.tier == "long_term" else config.SHORT_TERM_TIER_BONUS

        lexical = self._lexical_overlap(memory.content, query_text)
        relevance_gate = (semantic >= config.MIN_SEMANTIC_RELEVANCE) or (lexical >= 0.2)

        total = (
            config.SEMANTIC_WEIGHT * semantic
            + config.IMPORTANCE_WEIGHT * importance
            + config.FRESHNESS_WEIGHT * freshness
            + config.DECAY_BIAS_WEIGHT * decay_bias
            + tier_bonus
        )

        return {
            "semantic": semantic,
            "importance": importance,
            "freshness": freshness,
            "decay_bias": decay_bias,
            "tier_bonus": tier_bonus,
            "lexical": lexical,
            "relevance_gate": relevance_gate,
            "total": total,
        }

    def _build_trace(
        self,
        query: str,
        current_turn: int,
        elapsed: float,
        scored: List[Tuple[Memory, float, Dict[str, float]]],
        selected: List[Tuple[Memory, float, Dict[str, float]]],
        candidate_count: int
    ) -> Dict:
        top_breakdown = []
        for memory, score, detail in selected[:config.TRACE_TOP_N]:
            breakdown = {}
            for key, value in detail.items():
                if isinstance(value, bool):
                    breakdown[key] = value
                else:
                    breakdown[key] = round(value, 4)
            top_breakdown.append(
                {
                    "id": memory.id,
                    "content": memory.content[:120],
                    "tier": memory.tier,
                    "score": round(score, 4),
                    "breakdown": breakdown,
                }
            )

        return {
            "query": query,
            "turn": current_turn,
            "latency_ms": round(elapsed * 1000, 2),
            "candidate_count": candidate_count,
            "scored_count": len(scored),
            "selected_count": len(selected),
            "top": top_breakdown,
        }

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        similarity = dot_product / (mag1 * mag2)
        return (similarity + 1) / 2

    def _compute_freshness(self, memory: Memory) -> float:
        days_since_access = memory.days_since_access()
        return 1.0 / (1.0 + days_since_access)

    def _decay_bias(self, memory: Memory) -> float:
        days = memory.days_since_access()
        return max(0.0, 1.0 - (days * config.DECAY_RATE))

    def _lexical_overlap(self, a: str, b: str) -> float:
        a_tokens = set(self._tokenize(a))
        b_tokens = set(self._tokenize(b))
        if not a_tokens or not b_tokens:
            return 0.0
        return len(a_tokens & b_tokens) / len(a_tokens)

    def _tokenize(self, text: str) -> List[str]:
        cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return [tok for tok in cleaned.split() if len(tok) > 2]
