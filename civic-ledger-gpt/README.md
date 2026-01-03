Civic Ledger Actions Server (local-first)

Purpose
- Provide deterministic, schema-locked endpoints for Civic Ledger: ingest, search, extract, citation-validate, feasibility, and records-request templates.
- Designed to be imported as Custom GPT Actions (OpenAPI via FastAPI).

Quickstart
1) Create venv and install:
   python -m venv .venv
   . .venv/bin/activate
   pip install -e .

2) Build index from bundled data:
   civic-ledger-build-index --corpus ./data/records.jsonl --reddit ./data/reddit.jsonl --db ./civic_ledger.sqlite

3) Run API:
   civic-ledger-api --db ./civic_ledger.sqlite --host 127.0.0.1 --port 8787

OpenAPI
- Visit /docs for Swagger UI
- Export schema at /openapi.json

Notes
- This server does not do OCR. If a PDF has empty extracted text, extraction will return RED items.
- Citations are validated by exact substring match in stored normalized text.
