"""
Main Memory OS Application
Orchestrates the memory lifecycle with explainable retrieval.
"""

import os
import sys
import json
from typing import Dict, List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

sys.path.append(os.path.join(PROJECT_ROOT, "Storage Layer", "storage"))
sys.path.append(os.path.join(PROJECT_ROOT, "Memory System"))
sys.path.append(os.path.join(PROJECT_ROOT, "LLM Interface"))
sys.path.append(os.path.join(PROJECT_ROOT, "Configuration"))

from memory_store import MemoryStore
from llm.client import LLMClient
from memory.extractor import MemoryExtractor
from memory.scorer import MemoryScorer
from memory.retriever import MemoryRetriever
from memory.aging import MemoryAging
from memory.compressor import MemoryCompressor
from memory.injector import MemoryInjector
import config


class MemoryOS:
    """
    Main Memory Operating System.
    Coordinates all phases of memory lifecycle.
    """

    def __init__(self):
        print("Initializing Memory OS...")
        self.llm_client = LLMClient()
        self.turn_counter = 0

        self.memory_store = MemoryStore(self.llm_client)
        self.extractor = MemoryExtractor(self.llm_client)
        self.scorer = MemoryScorer(self.llm_client)
        self.retriever = MemoryRetriever(self.memory_store, self.llm_client)
        self.aging = MemoryAging(self.memory_store)
        self.compressor = MemoryCompressor(self.memory_store, self.llm_client)
        self.injector = MemoryInjector()

        self.analytics: Dict[str, float] = {
            "turns": 0,
            "stored": 0,
            "merged": 0,
            "conflicts_resolved": 0,
            "discarded": 0,
            "reinforced": 0,
            "reinforcement_delta": 0.0,
        }

        self.memory_store.load()
        self._boot_cleanup()

        stats = self.memory_store.get_stats()
        print(f"Memory OS ready. Loaded {stats['total_active']} active memories.")

    def _boot_cleanup(self):
        if config.DEBUG:
            print("Running boot cleanup...")
        self.memory_store.expire_memories()
        self.memory_store.apply_decay()
        self.memory_store.enforce_integrity()

    def process_turn(self, user_message: str):
        result = self.process_turn_with_metadata(user_message)
        if getattr(config, "EVAL_OUTPUT_MODE", False):
            return result
        return result["response_text"]

    def process_turn_with_metadata(self, user_message: str) -> Dict:
        self.turn_counter += 1
        current_turn = self.turn_counter
        self.analytics["turns"] += 1

        relevant_memories = self.retriever.retrieve(user_message, current_turn)
        memory_contents = [m.content for m in relevant_memories]
        response = self.llm_client.respond_with_context(user_message, memory_contents)

        candidates = self.extractor.extract(user_message, response)
        new_memories = self.scorer.batch_score(candidates, current_turn)

        for memory in new_memories:
            action, _ = self.memory_store.upsert_memory(memory, current_turn)
            if action == "added":
                self.analytics["stored"] += 1
            elif "merged" in action:
                self.analytics["merged"] += 1
            elif "conflict" in action:
                self.analytics["conflicts_resolved"] += 1
            else:
                self.analytics["discarded"] += 1

        if config.COMPRESSION_ENABLED and new_memories:
            for memory in new_memories:
                self.compressor.compress_if_needed(memory)

        self._reinforce_memories(relevant_memories)
        self.aging.on_turn()
        self._append_analytics_log(user_message, relevant_memories)

        if config.SAVE_EVERY_TURN:
            self.memory_store.save()

        return {
            "active_memories": self._format_active_memories(relevant_memories),
            "response_generated": bool(response and response.strip()),
            "response_text": response,
        }

    def _reinforce_memories(self, memories):
        if not getattr(config, "REINFORCEMENT_ENABLED", False):
            return
        for memory in memories:
            if getattr(config, "REINFORCEMENT_LONG_TERM_ONLY", False) and memory.tier != "long_term":
                continue
            if memory.confidence < getattr(config, "REINFORCEMENT_MIN_CONFIDENCE", 0.0):
                continue
            delta = getattr(config, "REINFORCEMENT_DELTA", 0.01) * (1.0 / (1.0 + memory.days_since_access()))
            memory.importance = min(1.0, memory.importance + delta)
            self.analytics["reinforced"] += 1
            self.analytics["reinforcement_delta"] += delta

    def _format_active_memories(self, memories: List) -> List[Dict]:
        formatted = []
        for memory in memories:
            formatted.append(
                {
                    "memory_id": memory.id,
                    "content": memory.content,
                    "origin_turn": memory.source_turn,
                    "last_used_turn": memory.last_used_turn,
                    "tier": memory.tier,
                    "importance": round(memory.importance, 4),
                    "confidence": round(memory.confidence, 4),
                }
            )
        return formatted

    def _append_analytics_log(self, query: str, relevant_memories):
        if not getattr(config, "ENABLE_ANALYTICS", False):
            return
        trace = self.retriever.get_last_trace()
        record = {
            "turn": self.turn_counter,
            "query": query,
            "retrieved_ids": [m.id for m in relevant_memories],
            "trace": trace,
            "analytics": self.analytics,
        }
        try:
            with open(config.ANALYTICS_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            if config.DEBUG:
                print("Failed to write analytics log.")

    def chat_loop(self):
        print("Memory OS Chat Interface")
        print("Commands: quit, stats, memories, trace, analytics, integrity, fresh, reset")

        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue

                lowered = user_input.lower()
                if lowered == "quit":
                    self.memory_store.save()
                    print("Goodbye")
                    break
                if lowered == "stats":
                    self._print_stats()
                    continue
                if lowered == "memories":
                    self._print_memories()
                    continue
                if lowered == "trace":
                    self._print_trace()
                    continue
                if lowered == "analytics":
                    self._print_analytics()
                    continue
                if lowered == "integrity":
                    self.memory_store.enforce_integrity()
                    print("Memory integrity checks applied.")
                    continue
                if lowered == "fresh":
                    self.retriever.query_cache.clear()
                    print("Fresh mode: retrieval cache cleared for a clean next response.")
                    continue
                if lowered == "reset":
                    confirm = input("Reset all memories? (yes/no): ")
                    if confirm.lower() == "yes":
                        self.memory_store.reset()
                        self.memory_store.save()
                        print("Memory store reset")
                    continue

                response = self.process_turn(user_input)
                print(f"Bot: {response}\n")
            except KeyboardInterrupt:
                self.memory_store.save()
                print("\nGoodbye")
                break
            except Exception as e:
                print(f"Error: {e}")
                if config.DEBUG:
                    import traceback
                    traceback.print_exc()

    def _print_stats(self):
        stats = self.memory_store.get_stats()
        print("\nMemory Statistics:")
        print(f"  Short-term: {stats['short_term_count']}")
        print(f"  Long-term: {stats['long_term_count']}")
        print(f"  Archived: {stats['archived_count']}")
        print(f"  Active: {stats['total_active']}")
        print(f"  Cache: {self.retriever.get_cache_stats()}\n")

    def _print_memories(self):
        memories = self.memory_store.get_all_memories()
        if not memories:
            print("\nNo memories stored yet\n")
            return

        print(f"\nStored Memories ({len(memories)} total)")
        print("=" * 60)
        for i, mem in enumerate(memories, 1):
            print(f"{i}. [{mem.tier}] {mem.content} | imp={mem.importance:.2f} conf={mem.confidence:.2f}")
        print()

    def _print_trace(self):
        trace = self.retriever.get_last_trace()
        if not trace:
            print("\nNo retrieval trace available yet.\n")
            return
        print("\nRetrieval Trace")
        print("=" * 60)
        print(f"Query: {trace.get('query')}")
        print(f"Turn: {trace.get('turn')}")
        print(f"Latency(ms): {trace.get('latency_ms')}")
        print(f"Candidates: {trace.get('candidate_count')} -> Scored: {trace.get('scored_count')}")
        for item in trace.get("top", []):
            print(f"- [{item['tier']}] score={item['score']} | {item['content']}")
            print(f"  breakdown={item['breakdown']}")
        print()

    def _print_analytics(self):
        print("\nAnalytics")
        print("=" * 60)
        for key, value in self.analytics.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
        print()


def main():
    try:
        memory_os = MemoryOS()
        memory_os.chat_loop()
    except Exception as e:
        print(f"Fatal error: {e}")
        if config.DEBUG:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
