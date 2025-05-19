# BUILD\_PLAN.md — PDB MCP Server

## Legend

| Icon | Meaning                        |
| ---- | ------------------------------ |
| 🛠   | Agent action (no human input)  |
| ❓    | Agent asks user a question     |
| ✍️   | Agent writes/edits a file      |
| ✅    | Verification / test checkpoint |

Agents repeat **Ask → Act → Verify** until every task passes.

---

## 0 · Environment Bootstrap

1. 🛠  Verify tools exist: `git ≥2.30`, `python3.11`, `pip`, `docker`, `docker compose`.
2. 🛠  `git config --global init.defaultBranch main` (if unset).
3. 🛠  Initialise repo: `git init pdb-mcp-server && cd pdb-mcp-server`.

✅ *Success when `git status` is clean inside new folder.*

---

## 1 · Generate Top‑Level Structure

1. 🛠  Create directories & files:

   ```bash
   mkdir -p .github/workflows mcp_pdb/{adapter,processing,utils} tests
   touch README.md BUILD_PLAN.md Dockerfile docker-compose.yml requirements.txt .github/workflows/ci.yml \
         mcp_pdb/__init__.py mcp_pdb/{main.py,config.py,schemas.py} \
         mcp_pdb/utils/cache.py mcp_pdb/adapter/pdb_client.py mcp_pdb/processing/dataset_builder.py \
         tests/{test_pdb_client.py,test_dataset_builder.py,test_integration.py}
   ```
2. 🛠  For **each directory just created** also `touch <dir>/README.md` (even for nested dirs).
3. ✅ *Pass when `tree -a -L 3` matches the scaffold above.*

---

## 2 · Populate Directory READMEs via Guided Q\&A

For **every directory** in breadth‑first order:

1. ❓  Ask user ➜ *“What is the primary purpose of `<dir>`? What key features, external systems, and design constraints should files here respect?”*
2. ✍️  Insert a **Context Block** at top of `<dir>/README.md`:

   ```md
   ## Context Summary
   *Purpose*: …
   *Interacts with*: …
   *Key features / constraints*: …
   *Relevant external dirs*: …
   ```

   (Fill blanks with user’s answers.)
3. ❓  Ask user ➜ *“List the files that must live in `<dir>` & one‑line function of each.”*
4. ✍️  Append a **Planned Files** table:

   ```md
   | File | Responsibility |
   |------|----------------|
   | foo.py | parse … |
   | …      | …           |
   ```
5. ✅ *Verify README has both Context Summary and Planned Files sections.*

*Repeat 2‑5 until every directory README is filled.*

---

## 3 · Create / Stub Files Described in READMEs

Iterate through READMEs’ **Planned Files** tables:

1. 🛠  For each listed file that doesn’t exist → create empty stub (respect package imports & module paths).
2. ✍️  Inside the README, under a **Status** column mark ✅ once file is created.
3. ✅ *Run `python -m compileall mcp_pdb` to ensure stubs are syntactically valid.*

---

## 4 · Implement Core Logic Incrementally

### 4.1 Adapter Layer (`mcp_pdb/adapter/pdb_client.py`)

1. ✍️  Implement async `fetch_entry` + `fetch_chem_comp` with `httpx`.
2. ✅  Unit test `tests/test_pdb_client.py` using `respx` to mock RCSB API.

### 4.2 Dataset Builder (`mcp_pdb/processing/dataset_builder.py`)

1. ✍️  Implement `build_structure_context` using adapter + cache.
2. ✅  Unit test with fixture JSON.

### 4.3 Cache Utility

1. ✍️  Implement simple FIFO/LRU cache per spec.
2. ✅  Unit test hit/miss & eviction.

### 4.4 FastAPI Entry (`mcp_pdb/main.py`)

1. ✍️  Define FastAPI app plus `/mcp` POST route performing JSON‑RPC dispatch.
2. ✅  Integration test posts example request → expect schema‑valid JSON. (Skipped locally due to terminal environment issues; will be tested in CI/cloud)

---

## 5 · Dependency & Formatting Setup

1. ✍️  Write `requirements.txt` with runtime & dev extras.
2. 🛠  `pip install -r requirements.txt`; run `black . && flake8`.
3. ✅  Lint passes; no `flake8` errors.

---

## 6 · Continuous Integration

1. ✍️  Populate `.github/workflows/ci.yml`:

   * Setup Python 3.11
   * `pip install -r requirements.txt`
   * `black --check . && flake8 .`
   * `pytest -q`
   * Build Docker image
2. ✅  Push branch ➜ GitHub Actions green.

---

## 7 · Containerisation

1. ✍️  Write **Dockerfile** (python:3.11‑slim, copy code, run uvicorn).
2. ✍️  Write **docker-compose.yml** exposing port `8000`.
3. 🛠  `docker compose up --build -d`.
4. ✅  `curl` test JSON‑RPC returns result.

---

## 8 · Robustness & Integration Checkpoints

| Checkpoint | When              | Command                        |
| ---------- | ----------------- | ------------------------------ |
| Syntax     | after every stub  | `python -m compileall mcp_pdb` |
| Unit tests | after each module | `pytest tests/<module>`        |
| Coverage   | pre‑merge         | `pytest --cov=mcp_pdb` ≥ 90%   |
| Lint       | each commit       | `flake8 .`                     |

---

## 9 · Iterative Agent Loop

1. Parse open `README.md` tasks.
2. Perform code/gen.
3. Run checkpoint commands.
4. If ✅ → commit; else fix until green.

Agents repeat until **all tests pass, container runs, CI green**.

---

## 10 · Finalise & Tag Release

1. 🛠  `git tag -a v0.1.0 -m "Minimal PDB MCP"`.
2. 🛠  Push tags; create GitHub release.
3. ✍️  Update top‑level `README.md` with badge links (CI, Docker size).

---

### Reference

*Follow design constraints & data mappings from DeepResearch technical report dated 2025‑05‑19.*

> **Done:** Windsurf agent now proceeds through sections 0‑10 sequentially, querying the user whenever ❓ steps appear, until repository is fully built and operational.
