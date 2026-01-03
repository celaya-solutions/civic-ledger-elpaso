# ---------- Build Stage ----------
FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy dependencies first for layer caching
COPY pyproject.toml requirements.txt ./
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt fastapi[standard] uvicorn pymupdf

# ---------- Runtime Stage ----------
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY server.py ./
COPY document_loader.py citation_validator.py template_generator.py feasibility_checker.py ./

# ✅ CRITICAL: Copy docs directory explicitly
COPY docs ./docs

# Copy any other necessary directories
COPY civic-ledger-gpt ./civic-ledger-gpt
COPY civic-server ./civic-server

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

CMD ["/app/.venv/bin/uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
