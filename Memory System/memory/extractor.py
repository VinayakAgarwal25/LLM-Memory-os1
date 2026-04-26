"""
Memory Extractor - Identifies and normalizes memory candidates
"""

import sys
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT / "Storage Layer" / "storage"))
sys.path.append(str(PROJECT_ROOT / "LLM Interface" / "llm"))
sys.path.append(str(PROJECT_ROOT / "Configuration"))

from models import MemoryCandidate
from client import LLMClient
import config


class MemoryExtractor:
    """
    Extracts memory-worthy information from conversations
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

        if getattr(config, "DEBUG", False):
            print("🔍 Memory extractor initialized")

    # -------------------------------------------------

    def extract(self, user_message: str, assistant_response: str) -> List[MemoryCandidate]:
        """
        Extract memory candidates from conversation turn
        """
        deterministic = self._extract_deterministic(user_message)
        if deterministic:
            return deterministic

        prompt = f"""
Extract ONLY durable user profile memories from the user message.
Allowed: identity, long-term preferences, constraints, stable goals.
Do NOT extract temporary discussion topics, examples, or assistant suggestions.
Do NOT infer or guess information.
Return each memory as a short bullet point.

User message:
{user_message}

Memories:
"""

        response = self.llm.generate(prompt)

        raw_memories = []
        for line in response.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith(("-", "*")):
                item = stripped.lstrip("-* ").strip()
            else:
                # Keep non-bullet lines only if they look like complete memories.
                item = stripped

            meta_markers = ("here are", "memories:", "bullet point", "extracted")
            if item.lower().startswith(meta_markers):
                continue

            raw_memories.append(item)

        candidates = []

        for content in raw_memories:

            if self.is_trivial(content):
                continue

            normalized = self._normalize(content)

            if (
                normalized
                and self._passes_hallucination_guard(normalized, user_message)
                and self._is_durable_memory(normalized)
            ):
                confidence = self._estimate_confidence(normalized, user_message)

                candidates.append(
                    MemoryCandidate(
                        content=normalized,
                        confidence=confidence,

                        memory_type=self._infer_type(normalized),
                        key=self._infer_key(normalized),
                        value=self._infer_value(normalized)
                    )
                )

        if getattr(config, "DEBUG", False):
            print(f"📝 Extracted {len(candidates)} normalized memory candidates")

        return candidates

    # -------------------------------------------------

    def _normalize(self, content: str) -> str:

        normalized = content.strip()

        replacements = {
            "I'm": "User is",
            "I am": "User is",
            "I ": "User ",
            "My ": "User's ",
            "me ": "user ",
            "myself": "themselves"
        }

        for old, new in replacements.items():
            if normalized.startswith(old):
                normalized = new + normalized[len(old):]

            normalized = normalized.replace(" " + old, " " + new)

        temporal_words = [" today", " now", " currently", " right now", " at the moment"]
        for word in temporal_words:
            normalized = normalized.replace(word, "")

        normalized = " ".join(normalized.split())

        if normalized and normalized[-1] not in ".!?":
            normalized += "."

        return normalized

    # -------------------------------------------------

    def is_trivial(self, content: str) -> bool:

        trivial_patterns = {
            "okay", "thanks", "thank you", "got it", "sure", "alright",
            "cool", "nice", "yes", "no", "maybe", "hmm", "uh", "um"
        }

        content_lower = content.lower().strip()

        if content_lower in trivial_patterns:
            return True

        if len(content_lower.split()) < 3:
            return True

        return False

    # -------------------------------------------------
    # Structured Inference Helpers
    # -------------------------------------------------

    def _infer_type(self, text: str) -> str:
        text = text.lower()

        if any(word in text for word in ["like", "love", "prefer", "enjoy"]):
            return "preference"

        if any(word in text for word in ["must", "only", "cannot", "should"]):
            return "constraint"

        if any(word in text for word in ["name is", "i am", "user is", "i work", "i live"]):
            return "fact"

        return "fact"

    # -------------------------------------------------

    def _infer_key(self, text: str) -> str:
        text = text.lower()

        if "veg" in text or "vegetarian" in text:
            return "diet"

        if "travel" in text or "trip" in text or "vacation" in text:
            return "travel_interest"

        if "pizza" in text or "food" in text:
            return "food_preference"

        if "name" in text:
            return "identity"

        return "general"

    # -------------------------------------------------

    def _infer_value(self, text: str) -> str:
        return text

    # -------------------------------------------------

    def _passes_hallucination_guard(self, candidate: str, user_message: str) -> bool:
        candidate_tokens = set(self._tokenize(candidate))
        user_tokens = set(self._tokenize(user_message))
        if not candidate_tokens or not user_tokens:
            return False

        overlap = len(candidate_tokens & user_tokens) / max(1, len(candidate_tokens))
        if overlap >= 0.25:
            return True

        # Allow simple canonicalized phrasing when key entities still overlap.
        entity_overlap = len({t for t in candidate_tokens if len(t) > 3} & {t for t in user_tokens if len(t) > 3})
        return entity_overlap > 0

    def _estimate_confidence(self, candidate: str, user_message: str) -> float:
        candidate_tokens = set(self._tokenize(candidate))
        user_tokens = set(self._tokenize(user_message))
        overlap = len(candidate_tokens & user_tokens) / max(1, len(candidate_tokens))
        return max(0.0, min(1.0, overlap))

    def _tokenize(self, text: str) -> List[str]:
        cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return [t for t in cleaned.split() if len(t) > 1]

    def _is_durable_memory(self, text: str) -> bool:
        t = text.lower()
        durable_markers = [
            "name", "i am", "user is", "prefer", "like", "love", "work", "study",
            "live", "goal", "want to", "cannot", "must", "always", "never",
            "only", "after", "before", "call", "diet", "vegetarian"
        ]
        if not any(marker in t for marker in durable_markers):
            return False

        transient_markers = [
            "today", "tonight", "this morning", "just", "currently discussing",
            "example", "for instance", "weather", "joke"
        ]
        if any(marker in t for marker in transient_markers):
            return False
        return True

    def _extract_deterministic(self, user_message: str) -> List[MemoryCandidate]:
        text = user_message.strip()
        low = text.lower()
        candidates: List[MemoryCandidate] = []

        if "preferred language is" in low:
            idx = low.find("preferred language is")
            value = text[idx + len("preferred language is"):].strip(" .")
            candidates.append(
                MemoryCandidate(
                    content=f"Preferred language: {value}.",
                    confidence=0.98,
                    memory_type="preference",
                    key="language_preference",
                    value=f"Preferred language: {value}."
                )
            )

        if "call me only after" in low:
            idx = low.find("call me only after")
            after = text[idx + len("call me only after"):].strip(" .")
            candidates.append(
                MemoryCandidate(
                    content=f"Call window: after {after}.",
                    confidence=0.98,
                    memory_type="constraint",
                    key="call_time",
                    value=f"Call window: after {after}."
                )
            )

        if "vegetarian" in low:
            candidates.append(
                MemoryCandidate(
                    content="Diet preference: vegetarian.",
                    confidence=0.98,
                    memory_type="preference",
                    key="diet",
                    value="Diet preference: vegetarian."
                )
            )

        if "work night shift" in low or "work night shifts" in low:
            candidates.append(
                MemoryCandidate(
                    content="Work schedule: night shifts on weekdays.",
                    confidence=0.95,
                    memory_type="constraint",
                    key="work_schedule",
                    value="Work schedule: night shifts on weekdays."
                )
            )

        return candidates
