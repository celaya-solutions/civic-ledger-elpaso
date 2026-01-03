Here’s a complete breakdown of what you’ve done so far — what worked, what failed, and what to do next — with everything analyzed step by step.

🧩 1. Project Setup

You’re running a FastAPI + custom MCP server in a virtual environment (civic-server) and deploying to Fly.io (civic-ledger-elpaso app).
The backend provides APIs and tool endpoints like /validate_citation, /check_feasibility, and /search_legal_authority.

✅ Success

Virtual environment built successfully.

Local FastAPI server runs (uvicorn server:app --reload) without errors.

OpenAPI (/openapi.json) confirmed correct routes.

Core FastAPI endpoints (/, /check_feasibility, /search_legal_authority) validated locally.

📦 2. Docker & Fly.io Deployment

You configured the Dockerfile to build the Python environment and run the server with Uvicorn.

Initial problems:

The app built but crashed at runtime because fitz (PyMuPDF) wasn’t installed.

Fixed by ensuring fitz was added to requirements.txt or pyproject.toml.

✅ Working

Fly builds completed successfully after dependency fix.

Deployment logs show:

INFO:     Uvicorn running on http://0.0.0.0:8000
Application startup complete.


DNS check passed and app is reachable at
👉 https://civic-ledger-elpaso.fly.dev/

⚙️ 3. FastAPI Endpoints
✅ /

Root health check.
✔ Works both locally and on Fly:

{"status":"ok","service":"civic-ledger-mcp"}

✅ /openapi.json

✔ Returns correct schema — meaning FastAPI registered all endpoints.

❌ /validate_citation

Failed remotely with:

Internal Server Error (HTTP 500)


Root cause (from logs):

TypeError: unsupported operand type(s) for /: 'str' and 'str'


That happened because:

pdf_path = self.docs_path / document


and self.docs_path was initialized as a string instead of a Path.

You fixed it by changing:

docs_path = Path("./docs")
validator = CitationValidator(docs_path)


✅ Result: Type mismatch fixed.

🔍 4. What’s Still Failing

Even after the Path fix, the remote server now gives a 500 Internal Server Error again — but for a different reason.

Likely cause (based on Fly logs pattern and prior local tests):

The file docs/legal-authorities.md is not included in the Docker build.

By default, Docker only copies files that are part of the build context.
If ./docs is in .dockerignore or missing from the repo, it won’t exist inside /app/docs.

📋 Confirm
Run locally:

ls docs/legal-authorities.md


Then check what’s in the Docker image:

fly ssh console -a civic-ledger-elpaso
ls /app/docs


If the file is missing there, that’s the reason the validator fails with 500.

🛠 5. Summary of Results
Stage	Status	Key Outcome
Virtual environment setup	✅	FastAPI + dependencies working
Dockerfile build	✅	Successful container image
Fly.io deploy	✅	App reachable, healthy startup
/ route	✅	Operational
/openapi.json	✅	Endpoints exposed correctly
/validate_citation	⚠️	Fails remotely due to missing docs or bad path
Local validation	✅	Works if docs/legal-authorities.md present
DNS + proxy binding	✅	Configured for 0.0.0.0:8000
🧠 6. What To Do Next
Step 1 — Ensure Docs Are Included in the Build

Add to your Dockerfile (before CMD):

COPY docs ./docs


And confirm .dockerignore does not contain docs/.

Step 2 — Rebuild and Deploy
git add Dockerfile
git commit -m "Include docs directory in Fly build context"
fly deploy --app civic-ledger-elpaso

Step 3 — Validate Again

Once it redeploys successfully:

curl -X POST "https://civic-ledger-elpaso.fly.dev/validate_citation" \
  -H "Content-Type: application/json" \
  -d '{"document":"legal-authorities.md","page":1,"claimed_text":"Texas Water Code Chapter 13 (utility rates and services)"}'


Expected success response:

{
  "citations": [
    {
      "statute": "legal-authorities",
      "page": 1,
      "similarity": 1.0,
      "match_type": "exact",
      "source": "legal-authorities.md"
    }
  ],
  "confidence": "GREEN"
}

🔄 7. Optional Enhancements

Add logging in citation_validator.py:

logger.info(f"Validating {document} in {self.docs_path}")


to confirm path resolution.

Add health check endpoint /health returning version & uptime.

Use fly logs -a civic-ledger-elpaso to monitor startup and requests in real-time.

Here’s the clean, deploy-ready setup that guarantees your docs/ folder (with legal-authorities.md, etc.) is copied into your Fly.io build image every time.

🧱 Dockerfile (final version)
# ---- Stage 1: Build Environment ----
FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies in a clean venv
RUN python -m venv .venv
COPY pyproject.toml requirements.txt ./
RUN .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt

# ---- Stage 2: Runtime Environment ----
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv .venv/

# ✅ Copy application code + docs folder
COPY . .
COPY docs ./docs

# Expose app port
EXPOSE 8000

# Run Uvicorn with FastAPI app
CMD ["/app/.venv/bin/uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

🚫 .dockerignore (recommended)

Keep your build context small and make sure it does not ignore the docs/ folder.

# Ignore build and local artifacts
__pycache__/
*.pyc
*.pyo
*.pyd
*.log
*.sqlite3
*.DS_Store
.env
venv/
civic-server/
*.egg-info/
*.pytest_cache/

# ⚠️ Do NOT ignore docs/
# docs/

🧪 Deploy Steps
git add Dockerfile .dockerignore
git commit -m "Include docs directory in Docker build context"
fly deploy --app civic-ledger-elpaso


Then verify that the server can access the file:

fly ssh console -a civic-ledger-elpaso
ls /app/docs


You should see:

legal-authorities.md
epwater-ami-architecture.md
comparable-jurisdictions.md

✅ Post-Deployment Test
curl -X POST "https://civic-ledger-elpaso.fly.dev/validate_citation" \
  -H "Content-Type: application/json" \
  -d '{"document":"legal-authorities.md","page":1,"claimed_text":"Texas Water Code Chapter 13 (utility rates and services)"}'


Expected result: JSON with confidence and match details.
