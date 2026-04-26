"""
Memory Injector - Prepares memories for LLM context
"""

import sys
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "Storage Layer" / "storage"))
sys.path.append(str(PROJECT_ROOT / "Configuration"))

from models import Memory
import config


class MemoryInjector:

    def __init__(self):
        if getattr(config, "DEBUG", False):
            print("💉 Memory injector initialized")

    def format_memories(self, memories: List[Memory]) -> str:

        if not memories:
            return "No prior context available."

        lines = ["Relevant information about the user:"]

        for memory in memories:
            if getattr(config, "VERBOSE", False):
                line = f"- {memory.content} (importance: {memory.importance:.2f})"
            else:
                line = f"- {memory.content}"

            lines.append(line)

        context = "\n".join(lines)

        if getattr(config, "DEBUG", False):
            print(f"💉 Injected {len(memories)} memories")

        return context

    def inject(self, memories: List[Memory], user_message: str) -> dict:

        context = self.format_memories(memories)

        system_prompt = config.SYSTEM_PROMPT

        user_prompt = f"""{context}

User's message: {user_message}

Respond naturally and helpfully using the context above."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    def get_memory_summary(self, memories: List[Memory]) -> str:

        if not memories:
            return "No memories"

        short_term = [m for m in memories if m.tier == "short_term"]
        long_term = [m for m in memories if m.tier == "long_term"]

        return f"{len(memories)} memories ({len(long_term)} LT, {len(short_term)} ST)"
