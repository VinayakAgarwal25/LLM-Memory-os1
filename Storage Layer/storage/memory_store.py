"""
Memory Store - Central storage manager for all memories.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from models import Memory
from vector_store import VectorStore
import config


class MemoryStore:
    """
    Central storage system for all memories.
    Manages short-term, long-term, and archived memories.
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.short_term: List[Memory] = []
        self.long_term: List[Memory] = []
        self.archived: List[Memory] = []
        self.vector_store = VectorStore(llm_client)

        os.makedirs(config.DATA_DIR, exist_ok=True)

        if config.DEBUG:
            print("Memory store initialized")

    def add_memory(self, memory: Memory):
        if memory.tier == "long_term":
            self.long_term.append(memory)
        else:
            self.short_term.append(memory)

        if memory.embedding:
            self.vector_store.add(memory.id, memory.embedding)

        if config.DEBUG:
            print(f"Added {memory.tier} memory: {memory.content[:50]}...")

    def upsert_memory(self, memory: Memory, current_turn: int) -> Tuple[str, Optional[str]]:
        """
        Add/update memory with deduplication and conflict resolution.
        Returns: (action, primary_memory_id).
        """
        if not memory.embedding:
            return "discarded_no_embedding", None

        similar = self.find_similar_memories(memory.embedding, top_k=8)
        if not similar:
            self.add_memory(memory)
            return "added", memory.id

        for existing, sim in similar:
            if sim < config.SIMILARITY_THRESHOLD:
                continue

            if self._is_conflict(existing, memory):
                winner = self._resolve_conflict(existing, memory)
                if winner.id == existing.id:
                    self._merge_memory(existing, memory, current_turn)
                    return "conflict_resolved_existing", existing.id
                self.remove_memory(existing.id)
                self.add_memory(memory)
                return "conflict_resolved_new", memory.id

            self._merge_memory(existing, memory, current_turn)
            return "merged_duplicate", existing.id

        self.add_memory(memory)
        return "added", memory.id

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        for memory in self.short_term + self.long_term + self.archived:
            if memory.id == memory_id:
                return memory
        return None

    def get_all_memories(self, include_archived: bool = False) -> List[Memory]:
        memories = self.short_term + self.long_term
        if include_archived:
            memories += self.archived
        return memories

    def remove_memory(self, memory_id: str):
        self.short_term = [m for m in self.short_term if m.id != memory_id]
        self.long_term = [m for m in self.long_term if m.id != memory_id]
        self.archived = [m for m in self.archived if m.id != memory_id]
        self.vector_store.remove(memory_id)

        if config.DEBUG:
            print(f"Removed memory {memory_id[:8]}")

    def archive_memory(self, memory_id: str):
        memory = self.get_memory(memory_id)
        if not memory:
            return

        self.short_term = [m for m in self.short_term if m.id != memory_id]
        self.long_term = [m for m in self.long_term if m.id != memory_id]
        if memory not in self.archived:
            self.archived.append(memory)
        self.vector_store.remove(memory_id)

        if config.DEBUG:
            print(f"Archived memory {memory_id[:8]}")

    def expire_memories(self):
        expired_count = 0
        for memory in self.short_term[:]:
            if memory.is_expired():
                self.archive_memory(memory.id)
                expired_count += 1
        if config.DEBUG and expired_count > 0:
            print(f"Expired {expired_count} memories")

    def apply_decay(self):
        all_memories = self.short_term + self.long_term
        for memory in all_memories:
            memory.apply_decay(config.DECAY_RATE)
            if memory.importance < config.MIN_IMPORTANCE_THRESHOLD:
                self.archive_memory(memory.id)
        if config.DEBUG:
            print(f"Applied decay to {len(all_memories)} memories")

    def find_duplicates(self, embedding: List[float], threshold: float = 0.9) -> List[str]:
        results = self.vector_store.search(embedding, k=5)
        return [mem_id for mem_id, sim in results if sim >= threshold]

    def find_similar_memories(self, embedding: List[float], top_k: int = 10) -> List[Tuple[Memory, float]]:
        similar = []
        for mem_id, sim in self.vector_store.search(embedding, k=top_k):
            memory = self.get_memory(mem_id)
            if memory:
                similar.append((memory, sim))
        return similar

    def save(self):
        self.enforce_integrity()
        data = {
            "short_term": [m.to_dict() for m in self.short_term],
            "long_term": [m.to_dict() for m in self.long_term],
            "archived": [m.to_dict() for m in self.archived],
            "last_saved": datetime.now().isoformat(),
        }

        try:
            with open(config.MEMORY_STORE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            if self.vector_store.index.ntotal > 0:
                self.vector_store.save(config.VECTOR_STORE_FILE)

            if config.VERBOSE:
                print(f"Saved memory store ({len(self.short_term)} ST, {len(self.long_term)} LT)")
        except Exception as e:
            print(f"Error saving memory store: {e}")

    def load(self):
        if not os.path.exists(config.MEMORY_STORE_FILE):
            if config.DEBUG:
                print("No existing memory store found, starting fresh")
            return

        try:
            with open(config.MEMORY_STORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.short_term = [Memory.from_dict(m) for m in data.get("short_term", [])]
            self.long_term = [Memory.from_dict(m) for m in data.get("long_term", [])]
            self.archived = [Memory.from_dict(m) for m in data.get("archived", [])]

            all_memories = self.short_term + self.long_term
            embeddings = [(m.id, m.embedding) for m in all_memories if m.embedding]
            if embeddings:
                self.vector_store.rebuild(embeddings)
            self.enforce_integrity()

            if config.VERBOSE:
                print(f"Loaded memory store ({len(self.short_term)} ST, {len(self.long_term)} LT)")
        except Exception as e:
            print(f"Error loading memory store: {e}")

    def search_vectors(self, query_embedding, top_k=50):
        if not query_embedding:
            return []
        matches = self.vector_store.search(query_embedding, k=top_k)
        results = []
        for memory_id, _ in matches:
            memory = self.get_memory(memory_id)
            if memory:
                results.append(memory)
        return results

    def get_stats(self) -> dict:
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "archived_count": len(self.archived),
            "total_active": len(self.short_term) + len(self.long_term),
            "vector_store": self.vector_store.get_stats(),
        }

    def reset(self):
        self.short_term = []
        self.long_term = []
        self.archived = []
        self.vector_store = VectorStore(self.llm_client)
        if config.DEBUG:
            print("Memory store reset")

    def enforce_integrity(self):
        """
        Enforce memory integrity and consistency constraints.
        """
        seen: Dict[str, int] = {}
        all_memories = self.get_all_memories(include_archived=True)
        for memory in all_memories:
            memory.importance = max(0.0, min(1.0, memory.importance))
            memory.confidence = max(0.0, min(1.0, memory.confidence))
            if memory.tier not in {"short_term", "long_term"}:
                memory.tier = "short_term"
            seen[memory.id] = seen.get(memory.id, 0) + 1
            if seen[memory.id] > 1:
                memory.id = f"{memory.id}-{seen[memory.id]}"

    def _merge_memory(self, existing: Memory, incoming: Memory, current_turn: int):
        existing.importance = min(1.0, max(existing.importance, incoming.importance))
        existing.confidence = max(existing.confidence, incoming.confidence)
        if incoming.confidence >= existing.confidence:
            existing.value = incoming.value
            existing.content = incoming.content
            existing.key = incoming.key
            existing.type = incoming.type
        if incoming.embedding:
            existing.embedding = incoming.embedding
            self.vector_store.add(existing.id, existing.embedding)
        existing.access(current_turn)

        if incoming.tier == "long_term" or existing.importance >= config.LONG_TERM_THRESHOLD:
            existing.tier = "long_term"
            existing.expiry = None
        elif existing.expiry is None and incoming.expiry is not None:
            existing.expiry = incoming.expiry

    def _is_conflict(self, a: Memory, b: Memory) -> bool:
        if a.key != b.key:
            return False
        if a.value.strip().lower() == b.value.strip().lower():
            return False
        return True

    def _resolve_conflict(self, a: Memory, b: Memory) -> Memory:
        score_a = (a.importance * 0.5) + (a.confidence * 0.3) + ((a.last_used_turn or 0) * 0.0005)
        score_b = (b.importance * 0.5) + (b.confidence * 0.3) + ((b.last_used_turn or 0) * 0.0005)
        return a if score_a >= score_b else b
