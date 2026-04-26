"""
Query-level LRU cache for retrieval results.
"""

from collections import OrderedDict
from typing import Any, Optional


class LRUCache:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self._store: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        value = self._store.pop(key)
        self._store[key] = value
        return value

    def set(self, key: str, value: Any):
        if key in self._store:
            self._store.pop(key)
        elif len(self._store) >= self.max_size:
            self._store.popitem(last=False)
        self._store[key] = value

    def clear(self):
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)
