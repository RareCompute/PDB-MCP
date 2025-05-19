# PDB-MCP v1.0 Release - TODO List

This document tracks outstanding tasks, untested elements, and necessary adjustments required for the PDB-MCP project to reach its v1.0 milestone.

## 1. Testing & Quality Assurance

- [ ] **Comprehensive Error Handling Tests**: Finalize and rigorously test error handling in `PDBClient` for all PDB API interactions (e.g., various HTTP error codes, malformed responses, network timeouts).
- [ ] **Integration Tests**: Develop more comprehensive integration tests that simulate end-to-end agent interactions with the FastAPI server, covering all MCP-compliant endpoints.
- [ ] **Unit Tests - `dataset_builder.py`**: Expand unit tests for `dataset_builder.py` to cover edge cases in data transformation and context assembly.
- [ ] **Unit Tests - `cache.py`**: Add detailed unit tests for `LRUCache` to ensure correct LRU eviction policy, `max_size` enforcement, and thread-safety if concurrent access is anticipated.
- [ ] **Unit Tests - `config.py`**: If any complex logic is added to `config.py`, ensure it's unit tested.
- [ ] **Performance Testing**: Conduct performance/load testing, especially focusing on the caching effectiveness and response times under typical and high load.

## 2. Core Functionality & Enhancements

- [ ] **Schema Review**: Thoroughly review and finalize Pydantic schemas in `mcp_pdb.schemas` for completeness, accuracy, and token efficiency. Consider any missing data fields crucial for BioML agents.
- [ ] **Additional PDB API Endpoints**: Evaluate the need for supporting additional PDB API endpoints (e.g., fetching full PDB files, sequence data, experimental method details) based on anticipated agent requirements.
- [ ] **MCP Compliance**: Formally define and document the JSON-RPC methods (`get_structure`, `get_ligand`, `search_structures`) ensuring full compliance with the Anthropic Model Context Protocol specification.
- [ ] **MCP-Compliant Integration**: Plan and begin implementation of any deeper MCP-compliant integration features beyond basic endpoint exposure.
- [ ] **Configuration Flexibility**: Ensure all key parameters (e.g., cache size, API timeouts, PDB API base URL) are easily configurable via environment variables or a central configuration file.

## 3. Documentation & Usability

- [ ] **End-User/Agent Developer Documentation**: Create high-level documentation guiding users (especially AI agent developers) on how to interact with the PDB-MCP service, including API endpoint details, request/response examples, and authentication/authorization if applicable.
- [ ] **Scientific Context**: Ensure all READMEs and documentation maintain clear scientific context as per Science Stanley's brand, making the project accessible and understandable.
- [ ] **`BUILD_PLAN.md` Review**: Update `BUILD_PLAN.md` to reflect the current project status and outline any remaining steps or changes for the v1.0 release.
- [ ] **Issue Templates**: Expand and refine the GitHub issue templates (`bug_report.md`, `feature_request.md`) in `.github/ISSUE_TEMPLATE/` for greater detail and clarity.

## 4. Infrastructure & Deployment

- [ ] **Docker Image Optimization**: Review and optimize the `Dockerfile` for image size and build speed.
- [ ] **Automated Docker Publishing**: If not already covered by `ci.yml`, set up automated building and publishing of Docker images to a registry (e.g., Docker Hub, GitHub Container Registry) upon new releases/tags.

## 5. Known Issues & Minor Fixes

- [ ] **Root `README.md` Trailing Space**: Investigate and resolve the persistent `MD009/no-trailing-spaces` lint error on line 3 of the root `README.md`.
- [ ] **Local Terminal SIGINT (130)**: While deferred, keep a note to investigate the local terminal environment issue causing commands to exit with code 130, as it might impact local development for some contributors.

---
*This list should be regularly reviewed and updated as the project progresses towards v1.0.*
