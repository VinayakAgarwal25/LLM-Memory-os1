"""
Memory Scorer - Evaluates importance of memory candidates
"""

import sys
from pathlib import Path
from typing import List
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "Storage Layer" / "storage"))
sys.path.append(str(PROJECT_ROOT / "LLM Interface" / "llm"))
sys.path.append(str(PROJECT_ROOT / "Configuration"))

from models import MemoryCandidate, Memory
from client import LLMClient
import config


class MemoryScorer:

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

        if getattr(config, "DEBUG", False):
            print("📊 Memory scorer initialized")

    # -------------------------------------------------

    def score(self, candidate: MemoryCandidate) -> float:

        prompt = f"""
Rate how important this user memory is for long-term personalization.
Return ONLY a number between 0 and 1.

Memory:
{candidate.content}

Score:
"""

        response = self.llm.generate(prompt)

        try:
            importance = float(response.strip())
        except:
            importance = 0.5

        importance *= getattr(candidate, "confidence", 1.0)
        if getattr(candidate, "confidence", 0.0) >= 0.95 and getattr(candidate, "type", "") in {"preference", "constraint", "fact"}:
            importance = max(importance, config.LONG_TERM_THRESHOLD)
        importance = max(0.0, min(1.0, importance))

        candidate.importance = importance
        return importance

    # -------------------------------------------------

    def classify_tier(self, importance: float) -> tuple:

        if importance >= config.LONG_TERM_THRESHOLD:
            tier = "long_term"
            expiry = None

        elif importance >= config.SHORT_TERM_THRESHOLD:
            tier = "short_term"
            expiry = datetime.now() + timedelta(days=config.SHORT_TERM_EXPIRY_DAYS)

        elif importance >= config.DISCARD_THRESHOLD:
            tier = "short_term"
            expiry = datetime.now() + timedelta(days=config.MEDIUM_TERM_EXPIRY_DAYS)

        else:
            if getattr(config, "DEBUG", False):
                print(f"🗑️ Discarding memory score {importance:.2f}")
            return None, None

        return tier, expiry

    # -------------------------------------------------

    def create_memory(
        self,
        candidate: MemoryCandidate,
        embedding: List[float],
        current_turn: int
    ) -> Memory:

        tier, expiry = self.classify_tier(candidate.importance)

        if tier is None:
            return None

        # ===== Structured Memory Creation =====
        memory = Memory(
            content=getattr(candidate, "value", candidate.content),
            importance=candidate.importance,
            tier=tier,

            # Structured fields
            memory_type=getattr(candidate, "type", "fact"),
            key=getattr(candidate, "key", "unknown"),
            value=getattr(candidate, "value", candidate.content),
            source_turn=current_turn,
            confidence=getattr(candidate, "confidence", 0.5),

            # Existing
            embedding=embedding,
            expiry=expiry
        )

        if getattr(config, "DEBUG", False):
            expiry_str = expiry.strftime("%Y-%m-%d") if expiry else "Never"
            print(
                f"✨ Created {tier} memory "
                f"(importance: {candidate.importance:.2f}, expires: {expiry_str})"
            )

        return memory

    # -------------------------------------------------

    def batch_score(
        self,
        candidates: List[MemoryCandidate],
        current_turn: int
    ) -> List[Memory]:

        memories = []

        for candidate in candidates:
            if getattr(candidate, "confidence", 0.0) < config.MIN_EXTRACTION_CONFIDENCE:
                if getattr(config, "DEBUG", False):
                    print(f"Skipping low-confidence candidate ({candidate.confidence:.2f})")
                continue

            self.score(candidate)

            if candidate.importance < config.MIN_STORAGE_CONFIDENCE:
                if getattr(config, "DEBUG", False):
                    print(f"Skipping low-storage-score candidate ({candidate.importance:.2f})")
                continue

            embedding = self.llm.embed(candidate.content)

            memory = self.create_memory(candidate, embedding, current_turn)

            if memory:
                memories.append(memory)

        if getattr(config, "DEBUG", False):
            print(f"📊 {len(candidates)} candidates → {len(memories)} memories")

        return memories
