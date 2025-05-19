import pytest
import time
import threading
from unittest.mock import patch

from mcp_pdb.utils.cache import LRUCache

@pytest.fixture
def cache():
    # Default cache for most tests
    return LRUCache(max_size=3, ttl_seconds=0.1) # Short TTL for testing expiry

@pytest.fixture
def no_ttl_cache():
    return LRUCache(max_size=3, ttl_seconds=10) # Longer TTL when expiry isn't the focus

def test_cache_set_get(no_ttl_cache: LRUCache):
    no_ttl_cache.set("key1", "value1")
    assert no_ttl_cache.get("key1") == "value1"
    assert "key1" in no_ttl_cache

def test_cache_miss(no_ttl_cache: LRUCache):
    assert no_ttl_cache.get("nonexistent_key") is None
    assert "nonexistent_key" not in no_ttl_cache

def test_cache_update_value(no_ttl_cache: LRUCache):
    no_ttl_cache.set("key1", "value1")
    no_ttl_cache.set("key1", "value2")
    assert no_ttl_cache.get("key1") == "value2"

def test_lru_eviction(no_ttl_cache: LRUCache):
    no_ttl_cache.set("key1", "value1")
    no_ttl_cache.set("key2", "value2")
    no_ttl_cache.set("key3", "value3")
    assert len(no_ttl_cache) == 3

    # Access key1 to make it most recently used
    no_ttl_cache.get("key1") 

    # Add a new key, should evict key2 (least recently used after key1 was touched)
    no_ttl_cache.set("key4", "value4")
    assert len(no_ttl_cache) == 3
    assert no_ttl_cache.get("key4") == "value4"
    assert no_ttl_cache.get("key2") is None # key2 should be evicted
    assert no_ttl_cache.get("key1") == "value1" # key1 should still be there
    assert no_ttl_cache.get("key3") == "value3" # key3 should still be there

def test_ttl_expiry(cache: LRUCache):
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    
    time.sleep(0.05) # Less than TTL
    assert cache.get("key1") == "value1"

    time.sleep(0.1) # Wait for TTL to expire (original TTL was 0.1)
    assert cache.get("key1") is None # Should be expired
    assert len(cache) == 0 # Length check also prunes

def test_cache_len(no_ttl_cache: LRUCache):
    assert len(no_ttl_cache) == 0
    no_ttl_cache.set("key1", "value1")
    no_ttl_cache.set("key2", "value2")
    assert len(no_ttl_cache) == 2
    no_ttl_cache.delete("key1")
    assert len(no_ttl_cache) == 1
    no_ttl_cache.clear()
    assert len(no_ttl_cache) == 0

@patch('mcp_pdb.utils.cache.CACHE_ENABLED', False)
def test_cache_disabled(no_ttl_cache: LRUCache):
    no_ttl_cache.set("key1", "value1")
    assert no_ttl_cache.get("key1") is None
    assert len(no_ttl_cache) == 0
    no_ttl_cache.clear() # Should not raise error
    no_ttl_cache.delete("key1") # Should not raise error

def test_init_invalid_max_size():
    with pytest.raises(ValueError, match="max_size must be a positive integer"):
        LRUCache(max_size=0, ttl_seconds=10)
    with pytest.raises(ValueError, match="max_size must be a positive integer"):
        LRUCache(max_size=-1, ttl_seconds=10)
    with pytest.raises(ValueError, match="max_size must be a positive integer"):
        LRUCache(max_size='abc', ttl_seconds=10)

def test_init_invalid_ttl():
    with pytest.raises(ValueError, match="ttl_seconds must be a positive number"):
        LRUCache(max_size=10, ttl_seconds=0)
    with pytest.raises(ValueError, match="ttl_seconds must be a positive number"):
        LRUCache(max_size=10, ttl_seconds=-1)
    with pytest.raises(ValueError, match="ttl_seconds must be a positive number"):
        LRUCache(max_size=10, ttl_seconds='abc')

def concurrent_task(cache, key_prefix, num_ops):
    for i in range(num_ops):
        key = f"{key_prefix}_{i}"
        cache.set(key, f"value_{i}")
        cache.get(key)

def test_thread_safety(no_ttl_cache: LRUCache):
    # Basic test for thread safety - not exhaustive but checks for obvious deadlocks/race conditions
    threads = []
    num_threads = 5
    ops_per_thread = 100

    for i in range(num_threads):
        thread = threading.Thread(target=concurrent_task, args=(no_ttl_cache, f"thread_{i}", ops_per_thread))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Check if cache size is within limits (max_size is 3 for no_ttl_cache)
    # Due to concurrency, exact final state can vary, but it shouldn't exceed max_size
    # and basic operations shouldn't have crashed.
    assert len(no_ttl_cache) <= no_ttl_cache.max_size
    # We can't easily assert specific items remain due to concurrent eviction
    # but we can check the cache is still functional
    no_ttl_cache.set("final_key", "final_value")
    assert no_ttl_cache.get("final_key") == "final_value"
