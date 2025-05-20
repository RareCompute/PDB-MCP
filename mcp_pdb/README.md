
# Context Summary

*Purpose*: 

This is the core Python package for the PDB-MCP server, designed to democratize access to structural biology data for AI/ML applications. It contains all application logic: API endpoints, PDB data fetching, data processing/caching, and schema definitions, enabling the creation of token-efficient datasets for BioML agents.

*Interacts with*: 
* External clients (e.g., BioML agents via HTTP GET to `/structure/{pdb_id}`)
* The RCSB PDB API (via `httpx`).

(Future: full MCP support via `/mcp` POST). The internal `LRUCache` is currently used, with potential for other cache backends.

*Key features / constraints*:
    1. Provides a FastAPI endpoint (`/structure/{pdb_id}`) for retrieving PDB data. (Future: Aims to fully implement Anthropic's Model Context Protocol (MCP) specification for JSON-RPC via an `/mcp` endpoint).
    2. Uses FastAPI for the web server and Pydantic for data validation/schemas.
    3. All PDB API interactions must be asynchronous (`async/await`).
    4. Code should be modular, with clear separation of concerns (adapter, processing, utils).
    5. Must be importable as a package (e.g., `import mcp_pdb`).
*Relevant external dirs*: `tests/` (for unit and integration tests), `Dockerfile` (for containerization), `requirements.txt` (for dependencies).

## Key Files and Their Roles

This table outlines the primary files and directories within `mcp_pdb` and their responsibilities:

| File / Directory                | Responsibility                                                                                                   |
|---------------------------------|------------------------------------------------------------------------------------------------------------------|
| `__init__.py`                   | Marks `mcp_pdb` as a Python package.                                                                             |
| `main.py`                       | FastAPI application entry point. Defines the `/structure/{pdb_id}` GET endpoint, global exception handlers, and application lifecycle events. (Future: `/mcp` POST for JSON-RPC).|
| `config.py`                     | Centralized application settings (e.g., API URLs, logging configuration, cache parameters) loaded from environment variables or defaults.|
| `schemas.py`                    | Pydantic models defining the structure of data (e.g., `StructureDataset`, `Ligand`) used within the application and returned by the API. These schemas are designed for clarity and token-efficiency.|
| `exceptions.py`                 | Defines custom exception classes for specific error conditions within the application, facilitating structured error handling (e.g., `PDBAPIError`, `NetworkError`, `DataValidationError`).|
| `README.md`                     | This file: Provides a high-level overview of the `mcp_pdb` package, its modules, and their roles.                |
| `utils/`                        | Sub-package containing shared utility modules.                                                                   |
|    └─ `utils/__init__.py`       | Marks `utils` as a Python sub-package.                                                                           |
|    └─ `utils/cache.py`          | Implements the `LRUCache` class with Time-To-Live (TTL) functionality for caching PDB API responses, improving performance and reducing redundant API calls.|
|    └─ `utils/README.md`         | Provides a context summary specifically for the `utils` sub-package and its contents.|
| `adapter/`                      | Sub-package responsible for interacting with external services, primarily the RCSB PDB API.                      |
|    └─ `adapter/__init__.py`     | Marks `adapter` as a Python sub-package.                                                                         |
|    └─ `adapter/pdb_client.py`   | Contains the `PDBClient` class, an asynchronous HTTP client for fetching data from the RCSB PDB API. It handles API communication, error parsing, and retries.|
|    └─ `adapter/README.md`       | Provides a context summary specifically for the `adapter` sub-package and its contents.|
| `processing/`                   | Sub-package containing logic for processing and transforming data obtained from external sources.              |
|    └─ `processing/__init__.py`  | Marks `processing` as a Python sub-package.                                                                      |
|    └─ `processing/dataset_builder.py` | Implements the `build_structure_context` function, which orchestrates fetching data (via `PDBClient`), utilizing the cache (`LRUCache`), and normalizing the raw PDB API response into the `StructureDataset` schema.|
|    └─ `processing/README.md`    | Provides a context summary specifically for the `processing` sub-package and its contents.|
