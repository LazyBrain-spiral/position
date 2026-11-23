# Multi-stage production Dockerfile for FastAPI API service
FROM python:3.11-slim AS builder

WORKDIR /workspace

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /bin/uv

# Copy workspace specifications
COPY pyproject.toml ./
COPY packages/ ./packages/
COPY apps/api/ ./apps/api/

# Sync dependencies
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Production runtime stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Security: Create non-root system user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Copy virtual environment and source code
COPY --from=builder /workspace/.venv /app/.venv
COPY --from=builder /workspace/apps/api/src /app/src
COPY --from=builder /workspace/packages /app/packages

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:/app/packages/contracts/src:/app/packages/common/src"
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/healthz || exit 1

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
