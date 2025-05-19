import time
from collections import OrderedDict
from typing import Any, Optional, Tuple
import threading

from mcp_pdb.config import CACHE_ENABLED, CACHE_MAX_SIZE, CACHE_TTL_SECONDS

class LRUCache:
    def __init__(self, max_size: int = CACHE_MAX_SIZE, ttl_seconds: int = CACHE_TTL_SECONDS):
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be a positive number")
            
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._cache = OrderedDict() # Stores key -> (value, expiry_time)
        self._lock = threading.Lock() # For thread safety

    def get(self, key: Any) -> Optional[Any]:
        if not CACHE_ENABLED:
            return None

        with self._lock:
            if key not in self._cache:
                return None

            value, expiry_time = self._cache[key]

            if time.time() > expiry_time:
                # Entry has expired
                del self._cache[key]
                return None
            
            # Move accessed item to the end to mark it as recently used
            self._cache.move_to_end(key)
            return value

    def set(self, key: Any, value: Any) -> None:
        if not CACHE_ENABLED:
            return

        with self._lock:
            expiry_time = time.time() + self.ttl
            
            if key in self._cache:
                # Key exists, update it and move to end
                del self._cache[key] # Remove to re-insert at the end
            elif len(self._cache) >= self.max_size:
                # Cache is full, remove the least recently used item (first item)
                self._cache.popitem(last=False)
            
            self._cache[key] = (value, expiry_time)

    def delete(self, key: Any) -> None:
        if not CACHE_ENABLED:
            return
        
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        with self._lock:
            # Prune expired items before returning length
            current_time = time.time()
            keys_to_delete = [
                k for k, (_, expiry) in self._cache.items() if expiry < current_time
            ]
            for k in keys_to_delete:
                del self._cache[k]
            return len(self._cache)

    def __contains__(self, key: Any) -> bool:
        return self.get(key) is not None # Relies on get() to handle expiry

# Optional: A global cache instance if desired, though often it's better to instantiate where needed.
# global_cache = LRUCache()
