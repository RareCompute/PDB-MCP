# PDB‑MCP Server

Democratising structural biology context for **BioML‑driven drug discovery** via Anthropic’s Model Context Protocol and the RCSB Protein Data Bank.

> *“Every scientist—human or machine—deserves friction‑free access to structural knowledge.”*

---

## 1 · Mission

Modern protein‐structure data powers generative chemistry, docking, and ML retrosynthesis. Yet most agents still screen‑scrape or download giant coordinate files. **PDB‑MCP** turns the RCSB Protein Data Bank into a *tool‑callable*, *token‑efficient*, and *cache‑friendly* source of truth. Running as a tiny FastAPI micro‑service, it exposes JSON‑RPC methods (`get_structure`, `get_ligand`, *optional* `search_structures`) that comply with Anthropic’s MCP spec—so any LLM agent can pull concise context bundles on‑demand.

The Rare Compute Foundation has built this project to support the **decentralised** and **equitable** development of BioML tools and agents in partnership with Bio.XYZ and as part of the Bio.XYZ Agents hackathon. Our design emphasises **decentralised** deployment (Docker or local CLI) so classrooms, hackerspaces, and startups can host their own mirror without central gatekeepers. Combined with open‑source code, this levels the playing field for global BioML research.

We will continue to develop and improve this project as part of our mission to support the development of equitable and decentralised BioML tools and agents, and will release it under the MIT license. Additional Rare Compute and Bio.XYZ will partner to deploy this system to serve a number of biologic compound design initatives within the DeSci space.

---

## 2 · Repository Map

| Path                                        | Purpose                                                                                                      |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **README.md**                               | You are here—top‑level overview, architecture, usage guides.                                                 |
| **BUILD\_PLAN.md**                          | Step‑by‑step Windsurf AI script that scaffolds directories, prompts for intent, stubs code, runs tests & CI. |
| **Dockerfile**                              | Container image (Python 3.11‑slim) running `uvicorn mcp_pdb.main:app`.                                       |
| **docker‑compose.yml**                      | One‑command local deployment; maps port 8000, sets env vars (cache size, log level).                         |
| **requirements.txt**                        | Runtime + dev dependencies (FastAPI, httpx, Pydantic, pytest, flake8, etc.).                                 |
| **.github/workflows/ci.yml**                | GitHub Actions: lint → tests → Docker build. Ensures every PR ships green.                                   |
| **mcp\_pdb/**init**.py**                    | Package marker & `__version__` string.                                                                       |
| **mcp_pdb/main.py**                        | FastAPI entrypoint. Defines the `/structure/{pdb_id}` GET endpoint for retrieving PDB data. (Future: full MCP JSON-RPC support via `/mcp` POST). |
| **mcp\_pdb/config.py**                      | Centralised settings (API base, cache size, env parsing).                                                    |
| **mcp\_pdb/schemas.py**                     | Pydantic models defining `StructureDataset`, `LigandDataset`, `Provenance`.                                  |
| **mcp\_pdb/utils/cache.py**                 | Tiny FIFO/LRU cache; pluggable store later (Redis, sqlite).                                                  |
| **mcp\_pdb/adapter/pdb\_client.py**         | Async wrapper over RCSB REST/GraphQL endpoints; handles retries & rate limits.                               |
| **mcp\_pdb/processing/dataset\_builder.py** | Normalises raw PDB JSON → token‑light context bundle; attaches provenance.                                   |
| **tests/**                                  | Pytest suite.                                                                                                |
|    └─ `test_pdb_client.py`                  | Mocks RCSB API via `respx`; verifies adapter logic.                                                          |
|    └─ `test_dataset_builder.py`             | Feeds fixture JSON into builder; asserts schema correctness.                                                 |
|    └─ `test_integration.py`                 | Full stack FastAPI client → JSON‑RPC request → validates result.                                             |

> **Directory READMEs** (generated via the build plan) embed *Context Summaries* so future agents immediately grasp local intent and file responsibilities.

---

## 3 · High‑Level Architecture

```mermaid
graph TD
Agent--JSON-RPC-->FastAPI[MCP Server]
FastAPI-->Adapter[PDBClient\nhttpx]
Adapter-->Assembler[Dataset Builder]
Assembler<-->Cache[LRU | disk]
```

*Call flow:* User/Agent requests `/structure/{pdb_id}` → Server fetches data via `PDBClient` (with integrated caching via `LRUCache`) → `DatasetBuilder` normalizes the raw PDB JSON into a token-efficient `StructureDataset` → Returns an ~2 KB JSON bundle (includes title, method, resolution, chains, ligands, and provenance).

---

## 4 · Quick Start (Linux)

```bash
git clone https://github.com/your-username-or-org/PDB-MCP.git
cd pdb-mcp-server
# dev venv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn mcp_pdb.main:app --reload
```

Test:

```bash
# Get structure data for PDB ID 1ABC
curl -s http://localhost:8000/structure/1ABC | jq
```

(Note: The MCP-standard JSON-RPC endpoint `/mcp` with POST requests is planned for future development. The current primary endpoint is GET `/structure/{pdb_id}`.)

Or launch in Docker:

```bash
docker compose up --build -d
```

---

## 5 · Using with LLMs and Agents

This PDB-MCP server provides structured, token-efficient data about protein structures, making it ideal for consumption by Large Language Models (LLMs) and autonomous agents in BioML research.

**Why token-efficient bundles?**
Concise data bundles are crucial for LLMs because they:

- Minimize the number of tokens processed, reducing API costs and latency.
- Fit critical information within the LLM's limited context window.
- Allow for more complex, multi-step reasoning by the agent (e.g., retrieve structure → analyze active sites → suggest ligands → evaluate docking potential).

**Current Usage (GET Endpoint):**
An agent can be programmed to make simple HTTP GET requests to the `/structure/{pdb_id}` endpoint:

*Example Python snippet for an agent:*

```python
import httpx

def get_pdb_structure_data(pdb_id: str):
    try:
        response = httpx.get(f"http://localhost:8000/structure/{pdb_id}")
        response.raise_for_status() # Raises an exception for 4XX/5XX errors
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        return None

# Example usage:
data = get_pdb_structure_data("1ABC")
if data:
    print(f"Title for 1ABC: {data.get('entry_title')}")
    print(f"Resolution: {data.get('resolution')}")
```

**Future: MCP-Compliant Agent Integration**
Future development aims to implement a full Model Context Protocol (MCP) compliant endpoint at `/mcp` (using JSON-RPC over POST). This will allow seamless integration with LLM agent frameworks that support MCP, such as those from Anthropic. 

Once implemented, you would typically:

1. **Register** the tool in your MCP host config:

   ```json
   {
     "servers": {
       "pdb": {"url": "http://localhost:8000/mcp"} 
     }
   }
   ```

2. In chat, an LLM could then be prompted (e.g., *“What is the resolution of 1ABC?”*), and it would internally make the appropriate JSON-RPC call to this server to retrieve the structured data and formulate an answer.

---

## 6 · Extending / Contributing

1. Fork ➜ branch ➜ `make lint test`.
2. Add or edit tests under `tests/`; maintain ≥90 % coverage.
3. Follow directory README context notes—**do not** introduce new files without updating the Planned Files table.
4. Open PR; CI must pass.

Roadmap ideas: streaming coordinate download, Redis cache backend, GraphQL search resource, private data servers and Web3 remuneration.
---

## 7 · License & Data Usage

Code: **MIT**.
PDB data: © RCSB Protein Data Bank — CC‑BY‑4.0; cite original authors when publishing.

---

## 8 · Acknowledgements

Built atop:

- Anthropic **Model Context Protocol**
- RCSB **Protein Data Bank** APIs
- FastAPI, Pydantic, httpx

Our gratitude to Bio.XYZ and the DeSci community for supporting **decentralised, equitable BioML**.
