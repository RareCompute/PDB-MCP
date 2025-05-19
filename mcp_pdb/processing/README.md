# Processing Sub-Package

This sub-package, `mcp_pdb.processing`, is dedicated to transforming raw data obtained from external sources (like the PDB API via the `adapter` package) into the structured, token-efficient formats required by the PDB-MCP application and its clients (e.g., BioML agents).

## Key Components

### `dataset_builder.py` - Contextual Data Builder

- **Purpose**: Contains the core logic for constructing the final data payloads. The primary function here is `build_structure_context`.
- **Functionality**:
  - Orchestrates the data fetching process by utilizing `PDBClient` from the `mcp_pdb.adapter` package to retrieve necessary information (e.g., entry summary, non-polymer entity details) for a given PDB ID.
  - Integrates with the `LRUCache` (from `mcp_pdb.utils.cache`) to cache responses from the PDB API, reducing redundant calls and improving performance.
  - Normalizes and transforms the raw JSON data fetched from the PDB API into the Pydantic models defined in `mcp_pdb.schemas` (e.g., `StructureDataset`, `Ligand`). This step ensures data consistency, validation, and prepares the data in a token-efficient manner suitable for LLM consumption.
  - Assembles the final context bundle, potentially including provenance information about the data sources and processing steps.
- **Usage**: The `build_structure_context` function is called by the API endpoint handlers in `mcp_pdb.main.py` when a request for a PDB structure's context is received.

### `__init__.py`

- Marks the `processing` directory as a Python sub-package, allowing its modules and functions (like `build_structure_context`) to be imported and used by other parts of the `mcp_pdb` application.

The `processing` package plays a vital role in ensuring that the data provided by the PDB-MCP server is not only accurate but also structured optimally for AI/ML applications, aligning with the project's goal of facilitating BioML research and discovery.
