"""
Data models for Memory OS
Defines the structure of memory objects
"""

import uuid
from datetime import datetime
from typing import Optional, List


# =========================================================
# Memory Object
# =========================================================

class Memory:
    """
    Structured memory object aligned with hackathon specification
    """

    def __init__(
        self,
        content: str,
        importance: float,
        tier: str,

        # Structured fields
        memory_type: str = "fact",
        key: str = "unknown",
        value: str = "",
        source_turn: int = 0,
        confidence: float = 1.0,

        # Storage fields
        embedding: Optional[List[float]] = None,
        memory_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        last_accessed: Optional[datetime] = None,
        expiry: Optional[datetime] = None,
        access_count: int = 0,

        # Usage tracking
        last_used_turn: Optional[int] = None,
        usage_count: int = 1
    ):

        self.id = memory_id or str(uuid.uuid4())

        # Natural content
        self.content = content

        # Structured fields
        self.type = memory_type
        self.key = key
        self.value = value or content
        self.source_turn = source_turn
        self.confidence = confidence

        # Scoring
        self.importance = max(0.0, min(1.0, importance))
        self.tier = tier

        # Embedding
        self.embedding = embedding or []

        # Time tracking
        self.created_at = created_at or datetime.now()
        self.last_accessed = last_accessed or datetime.now()
        self.expiry = expiry
        self.access_count = access_count

        # Usage tracking
        self.last_used_turn = last_used_turn if last_used_turn is not None else source_turn
        self.usage_count = usage_count

    # -------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize memory for storage"""

        return {
            "id": self.id,
            "content": self.content,

            # Structured
            "type": self.type,
            "key": self.key,
            "value": self.value,
            "source_turn": self.source_turn,
            "confidence": self.confidence,

            # Scoring
            "importance": self.importance,
            "tier": self.tier,

            # Vector
            "embedding": self.embedding,

            # Time
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "access_count": self.access_count,

            # Usage
            "last_used_turn": self.last_used_turn,
            "usage_count": self.usage_count
        }

    # -------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "Memory":
        """Load memory safely from disk"""

        return cls(
            memory_id=data.get("id"),
            content=data.get("content", ""),
            importance=data.get("importance", 0.5),
            tier=data.get("tier", "short_term"),

            memory_type=data.get("type", "fact"),
            key=data.get("key", "unknown"),
            value=data.get("value", data.get("content", "")),
            source_turn=data.get("source_turn", 0),
            confidence=data.get("confidence", 0.5),

            embedding=data.get("embedding", []),

            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at") else datetime.now(),

            last_accessed=datetime.fromisoformat(data["last_accessed"])
            if data.get("last_accessed") else datetime.now(),

            expiry=datetime.fromisoformat(data["expiry"])
            if data.get("expiry") else None,

            access_count=data.get("access_count", 0),
            last_used_turn=data.get("last_used_turn"),
            usage_count=data.get("usage_count", 1)
        )

    # -------------------------------------------------

    def is_expired(self) -> bool:
        if self.expiry is None:
            return False
        return datetime.now() > self.expiry

    # -------------------------------------------------

    def access(self, current_turn: Optional[int] = None):
        """Mark memory as accessed safely"""

        self.last_accessed = datetime.now()
        self.access_count += 1

        if current_turn is not None:
            self.last_used_turn = current_turn
            self.usage_count += 1

    # -------------------------------------------------

    def days_since_access(self) -> int:
        return (datetime.now() - self.last_accessed).days

    # -------------------------------------------------

    def apply_decay(self, decay_rate: float):
        days = self.days_since_access()
        decay_factor = max(0.0, min(1.0, 1.0 - decay_rate))
        self.importance *= (decay_factor ** days)
        self.importance = max(0.0, min(1.0, self.importance))

    # -------------------------------------------------

    def __repr__(self):
        return (
            f"Memory(id={self.id[:8]}, type={self.type}, key={self.key}, "
            f"importance={self.importance:.2f}, tier={self.tier}, "
            f"value='{self.value[:40]}...')"
        )


# =========================================================
# Memory Candidate
# =========================================================

class MemoryCandidate:
    """
    Temporary structured memory candidate
    """

    def __init__(
        self,
        content: str,
        confidence: float = 1.0,
        memory_type: str = "fact",
        key: str = "unknown",
        value: str = ""
    ):

        self.content = content
        self.confidence = confidence
        self.type = memory_type
        self.key = key
        self.value = value or content
        self.importance = None

    def __repr__(self):
        return (
            f"MemoryCandidate(type={self.type}, key={self.key}, "
            f"value='{self.value}', confidence={self.confidence})"
        )
