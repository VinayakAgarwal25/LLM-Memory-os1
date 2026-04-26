"""
Memory Aging - Handles decay and forgetting
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "Storage Layer" / "storage"))
sys.path.append(str(PROJECT_ROOT / "Configuration"))

from memory_store import MemoryStore
import config


class MemoryAging:

    def __init__(self, memory_store: MemoryStore):
        self.store = memory_store
        self.turn_counter = 0

        if getattr(config, "DEBUG", False):
            print("⏳ Memory aging initialized")

    def age_memories(self):

        if not config.AGING_ENABLED:
            if getattr(config, "DEBUG", False):
                print("⏳ Aging disabled, skipping")
            return

        self.store.expire_memories()
        self.store.apply_decay()

        self._forget_low_importance()
        self._archive_stale_long_term()

        if getattr(config, "DEBUG", False):
            stats = self.store.get_stats()
            print(f"⏳ Aging complete (Active: {stats['total_active']}, Archived: {stats['archived_count']})")

    def _forget_low_importance(self):

        forgotten_count = 0

        all_memories = self.store.get_all_memories(include_archived=False)

        for memory in all_memories:
            if memory.importance < config.MIN_IMPORTANCE_THRESHOLD:
                self.store.archive_memory(memory.id)
                forgotten_count += 1

        if getattr(config, "DEBUG", False) and forgotten_count > 0:
            print(f"🧹 Forgot {forgotten_count} low-importance memories")

    def on_turn(self):

        self.turn_counter += 1

        if self.turn_counter % config.RUN_AGING_EVERY_N_TURNS == 0:
            self.age_memories()

    def force_age(self):
        self.age_memories()

    def _archive_stale_long_term(self):
        archived = 0
        for memory in self.store.long_term[:]:
            days_idle = memory.days_since_access()
            if (
                days_idle >= config.LONG_TERM_ARCHIVE_DAYS
                and memory.importance < config.LONG_TERM_MIN_IMPORTANCE_TO_KEEP
            ):
                self.store.archive_memory(memory.id)
                archived += 1

        if getattr(config, "DEBUG", False) and archived:
            print(f"Archived {archived} stale long-term memories")
