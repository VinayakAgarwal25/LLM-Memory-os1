"""
Memory Compressor - Merges similar memories
"""

import sys
from pathlib import Path
from typing import List
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "Storage Layer" / "storage"))
sys.path.append(str(PROJECT_ROOT / "LLM Interface" / "llm"))
sys.path.append(str(PROJECT_ROOT / "Configuration"))

from memory_store import MemoryStore
from models import Memory
from client import LLMClient
import config


class MemoryCompressor:

    def __init__(self, memory_store: MemoryStore, llm_client: LLMClient):
        self.store = memory_store
        self.llm = llm_client

        if getattr(config, "DEBUG", False):
            print("🗜️ Memory compressor initialized")

    def compress_if_needed(self, new_memory: Memory):

        if not config.COMPRESSION_ENABLED:
            return False

        similar_ids = self.store.find_duplicates(
            new_memory.embedding,
            threshold=config.SIMILARITY_THRESHOLD
        )

        if not similar_ids:
            return False

        similar_memories = [self.store.get_memory(mid) for mid in similar_ids]
        similar_memories = [m for m in similar_memories if m]

        # Include the new memory if it's not already in results.
        all_memories = {m.id: m for m in similar_memories}
        all_memories[new_memory.id] = new_memory

        if len(all_memories) < config.MIN_MEMORIES_FOR_COMPRESSION:
            return False

        self._compress_memories(list(all_memories.values()))
        return True

    def _compress_memories(self, memories: List[Memory]):

        if len(memories) < 2:
            return

        if getattr(config, "DEBUG", False):
            print(f"🗜️ Compressing {len(memories)} memories...")

        contents = [m.content for m in memories]

        prompt = f"""
Merge these similar user memories into ONE concise factual memory.

Memories:
{chr(10).join(contents)}

Compressed memory:
"""

        compressed_content = self.llm.generate(prompt).strip()

        if not compressed_content:
            return

        new_importance = max(m.importance for m in memories)
        new_importance = min(1.0, new_importance + 0.05)

        if new_importance >= config.LONG_TERM_THRESHOLD:
            tier = "long_term"
            expiry = None
        else:
            tier = "short_term"
            expiries = [m.expiry for m in memories if m.expiry]
            expiry = max(expiries) if expiries else (datetime.now() + timedelta(days=config.SHORT_TERM_EXPIRY_DAYS))

        compressed_embedding = self.llm.embed(compressed_content)
        compressed_memory = Memory(
            content=compressed_content,
            importance=new_importance,
            tier=tier,
            memory_type="summary",
            key="compressed",
            value=compressed_content,
            source_turn=max((m.source_turn for m in memories), default=0),
            confidence=max((m.confidence for m in memories), default=0.7),
            embedding=compressed_embedding,
            expiry=expiry
        )

        # Remove originals and insert compressed replacement.
        for memory in memories:
            self.store.remove_memory(memory.id)

        self.store.add_memory(compressed_memory)

        if getattr(config, "DEBUG", False):
            print(f"🗜️ Compressed {len(memories)} memories into 1 ({tier})")
