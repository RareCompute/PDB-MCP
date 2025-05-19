# Context Summary

*Purpose*: Serve as the automated safety net that verifies every core module of the PDB-MCP server behaves as expected—unit, integration, and regression tests run locally and in CI.
*Key features / constraints*:
    *Pytest-based suites with clear naming (test_*.py).
    *Use respx or httpx.MockTransport to stub RCSB API calls—tests must never hit the live internet.
    *Coverage threshold ≥ 90 % enforced in CI.
    *Separation of concerns: adapter tests, builder tests, integration (FastAPI) tests.
    *Deterministic: no network, random, or time-based flakiness.
    *Fast: suite must finish in <60 s on ubuntu-latest.
    *Self-contained fixtures—no large binary data; embed minimal JSON samples.
    *Keep test directory import-safe (avoid altering sys.path, rely on installed mcp_pdb package).
*Interacts with*: GitHub Actions runner (CI), FastAPI TestClient (in-process server), respx/mock transport for RCSB endpoints, coverage tooling.
*Relevant external dirs*: `mcp_pdb/` (the code being tested), `.github/workflows/ci.yml` (where these tests will be executed).

## Key Files and Their Roles

| File / Path                 | Responsibility                                                                                                |
|-----------------------------|---------------------------------------------------------------------------------------------------------------|
| tests/README.md             | Holds the Context Summary (above) and this Planned Files table for quick agent reference.                     |
| tests/__init__.py           | Marks the folder as a Python package so pytest can resolve relative imports.                                  |
| tests/conftest.py           | Shared fixtures and sample JSON payloads reused across unit and integration suites.                           |
| tests/test_pdb_client.py    | Unit-tests mcp_pdb.adapter.pdb_client.PDBClient using respx mocks; checks happy-path and error handling.        |
| tests/test_dataset_builder.py | Unit-tests mcp_pdb.processing.dataset_builder.build_structure_context; validates schema, cache hit/miss behaviour. |
| tests/test_integration.py   | Spins up FastAPI TestClient, sends a GET request to the `/structure/{pdb_id}` endpoint, asserts a 200 OK response, and validates that the output matches the `StructureDataset` model. |
