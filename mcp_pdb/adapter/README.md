# Adapter Sub-Package

This sub-package, `mcp_pdb.adapter`, is responsible for all interactions with external services, primarily the RCSB Protein Data Bank (PDB) API. It acts as a translation layer, abstracting the complexities of external APIs and providing a consistent interface for the rest of the PDB-MCP application.

## Key Components

### `pdb_client.py` - PDB API Client

- **Purpose**: Contains the `PDBClient` class, which is an asynchronous HTTP client specifically designed to fetch data from the various RCSB PDB API endpoints (e.g., summary, entry, non-polymer entity data).
- **Functionality**:
  - Constructs appropriate API request URLs based on PDB IDs and desired data types.
  - Handles HTTP GET requests asynchronously using `httpx`.
  - Implements error handling for API-specific errors (e.g., 404 Not Found for invalid PDB IDs, 429 Too Many Requests) and network issues, leveraging custom exceptions defined in `mcp_pdb.exceptions`.
  - Parses JSON responses from the PDB API.
  - Includes retry mechanisms for transient network errors (though this might be more explicitly managed or configured at a higher level or via `httpx` transport settings).
- **Usage**: The `PDBClient` is utilized by the `dataset_builder.py` in the `mcp_pdb.processing` package to retrieve the raw data needed to construct token-efficient context bundles for BioML agents.

### `__init__.py`

- Marks the `adapter` directory as a Python sub-package, allowing its modules (like `PDBClient`) to be imported elsewhere in the `mcp_pdb` application.

By encapsulating external API interactions here, the `adapter` package promotes modularity and makes it easier to manage, update, or even replace external data sources without significantly impacting other parts of the application.
