# Repository Guidelines

## Project Structure & Module Organization
- `src/civic_ledger_actions`: FastAPI actions server (ingest, search, extract, feasibility, records templates); SQLite access in `storage.py`, ingestion helpers in `indexer.py`, extraction/citation logic in `extract.py` and `citations.py`.
- `server.py`: MCP server wiring document search, citation validation, and policy packet assembly; relies on `docs/` content and vector index state under `.chroma` in that folder.
- `docs/` and `examples/`: Reference materials and sample outputs that feed prompts; keep citations intact.
- `dc_corpus/` and `graphs/`: Source corpus and derived artifacts; treat as data, not code.
- `scripts/run_local.sh` and `civic-ledger-gpt/`: Packaged copy of the actions server with console scripts; use this when you want the CLI entry points.

## Setup, Build, and Development Commands
- Use Python 3.11+. Create an environment: `python -m venv .venv && source .venv/bin/activate`.
- Install runtime + dev deps for the actions API: `pip install -e civic-ledger-gpt` (provides `civic-ledger-api` and `civic-ledger-build-index`) and `pip install -r requirements.txt` for scraping utilities. Add `pip install pytest black ruff` if not already present.
- Build a local index (expects `data/records.jsonl` and optional `data/reddit.jsonl`): `civic-ledger-build-index --corpus ./data/records.jsonl --reddit ./data/reddit.jsonl --db ./civic_ledger.sqlite`.
- Run the API: `civic-ledger-api --db ./civic_ledger.sqlite --host 127.0.0.1 --port 8787` (Swagger at `/docs`). `scripts/run_local.sh` chains index + API startup.
- MCP server (experimental): ensure deps from `pyproject.toml` are installed, then run with `python -m server` from the repo root; it serves tools that read from `docs/`.

## Coding Style & Naming Conventions
- Python with type hints and Pydantic models; prefer 4-space indentation and explicit return types.
- Follow FastAPI conventions for route naming (`snake_case` paths, verb-noun handlers). Keep schemas in `models.py`; reuse `BaseModel` classes across handlers.
- Run `black` and `ruff` before sending changes; keep SQL strings parameterized as in `storage.py`.

## Testing Guidelines
- Framework: `pytest`. Co-locate tests next to modules or under a `tests/` folder you create.
- Add unit coverage for new ingest/search/extraction helpers; mock filesystem/DB where possible. For API routes, use FastAPI’s `TestClient`.
- Run `pytest` before PRs; include sample DB fixtures or trimmed `records.jsonl` snippets for deterministic assertions.

## Commit & Pull Request Guidelines
- Use concise, present-tense commits (e.g., `feat: add feasibility check coverage`, `fix: guard empty search queries`). Reference tickets/issues in the body when relevant.
- PRs should describe intent, testing performed (`pytest`, manual curl against `/health`), and any schema changes. Attach sample requests/responses for new endpoints.
- Avoid committing generated databases (`civic_ledger.sqlite*`) or large corpus files; prefer instructions for regeneration.
