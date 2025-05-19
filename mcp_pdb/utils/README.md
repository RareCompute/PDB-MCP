# Utilities Sub-Package

This sub-package, `mcp_pdb.utils`, provides common utility functions and classes that are used across various parts of the PDB-MCP application. These utilities help in promoting code reuse and abstracting common functionalities.

## Key Components

### `cache.py` - LRU Cache Implementation

- **Purpose**: Contains the `LRUCache` class, an in-memory cache with a Least Recently Used (LRU) eviction policy. This cache is primarily used to store responses from the RCSB PDB API to reduce redundant API calls, improve response times, and stay within API rate limits.
- **Functionality**:
  - Implements a dictionary-backed cache with a configurable `max_size`.
  - When the cache reaches its `max_size`, the least recently used item is evicted to make space for new items.
  - Provides `get(key)` and `put(key, value)` methods for cache operations.
  - The `get` operation also marks the accessed item as recently used.
  - It is designed to store arbitrary data, but in the context of PDB-MCP, it caches JSON responses from the PDB API, where keys are typically API URLs or derived identifiers, and values are the fetched JSON data.
- **Usage**: An instance of `LRUCache` is typically initialized in `mcp_pdb.main.py` or `mcp_pdb.config.py` and then passed to or accessed by the `PDBClient` (in `mcp_pdb.adapter.pdb_client`) and/or `dataset_builder.py` (in `mcp_pdb.processing`) to cache API call results. The cache size can be configured via environment variables or application settings.

### `__init__.py`

- Marks the `utils` directory as a Python sub-package, allowing its modules and classes (like `LRUCache`) to be imported and utilized by other components of the `mcp_pdb` application.

The `utils` package enhances the modularity and efficiency of the PDB-MCP application by providing well-defined, reusable utility components like the caching mechanism.
