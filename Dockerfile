# ---------- Build Stage ----------
FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy dependencies
COPY pyproject.toml requirements.txt ./
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt fastapi[standard] uvicorn pymupdf

# ---------- Runtime Stage ----------
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy ONLY essential files for the server to run
COPY server.py document_loader.py citation_validator.py template_generator.py feasibility_checker.py ./

# ✅ CRITICAL: Copy docs directory for citations
COPY docs ./docs

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

CMD ["/app/.venv/bin/uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
