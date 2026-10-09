"""
In-memory cache for expensive dataset aggregations.
All cache entries are populated lazily on first request and held in RAM.
"""

import threading
from typing import Any, Dict, Optional

_lock  = threading.Lock()
_store: Dict[str, Any] = {}


def get(key: str) -> Optional[Any]:
    return _store.get(key)


def set(key: str, value: Any) -> None:
    with _lock:
        _store[key] = value


def has(key: str) -> bool:
    return key in _store


def clear(key: Optional[str] = None) -> None:
    with _lock:
        if key:
            _store.pop(key, None)
        else:
            _store.clear()
