# ── Build stage ──────────────────────────────────────────────────────────────
FROM --platform=linux/amd64 python:3.13-slim-bookworm AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM --platform=linux/amd64 python:3.13-slim-bookworm

# Build-time arguments for OCI image labels
ARG BUILD_DATE
ARG GIT_SHA

# OCI standard labels for version control traceability
LABEL org.opencontainers.image.title="mcp-server-py-bank-of-canada-valet" \
      org.opencontainers.image.description="MCP Server for Bank of Canada exchange rates via the Valet API" \
      org.opencontainers.image.source="https://github.com/bill-ying/mcp-server-py-bank-of-canada-valet" \
      org.opencontainers.image.licenses="GPL-3.0-or-later" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${GIT_SHA}"

# Non-root user for security
RUN groupadd --gid 1000 appuser && \
    useradd  --uid 1000 --gid appuser --shell /bin/sh --create-home appuser

# Upgrade all packages to pull in security patches (fixes libgnutls30 CVE),
# then install curl for the health check.
RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY src/ ./src/

# Python path so uvicorn can resolve the package
ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 7860

# curl with a 3-second timeout avoids hanging on the SSE stream.
# -o /dev/null discards the body; -s suppresses progress output.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --max-time 3 --silent http://localhost:7860/sse -o /dev/null || exit 1

CMD ["uvicorn", "mcp_server_bank_of_canada.server:app", "--host", "0.0.0.0", "--port", "7860"]
