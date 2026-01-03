# ---------- Build Stage ----------
FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml requirements.txt ./
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt fastapi[standard] uvicorn

# ---------- Runtime Stage ----------
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
