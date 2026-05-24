---
title: Bank of Canada Valet MCP Server
emoji: 🍁
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 7860
---

# Bank of Canada Valet MCP Server

> A [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that provides historical exchange rates from the [Bank of Canada Valet API](https://www.bankofcanada.ca/valet/). Deployed as a Docker container on **Hugging Face Spaces**.

## Overview

This is an idiomatic Python MCP server built with the official [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk) (`FastMCP`). It leverages Python's native type hinting and FastMCP's straightforward decorators to provide a lightweight, high-performance integration.

## Available Tools

### `get_exchange_rate`

Retrieves the exchange rate between USD and CAD for a specific date.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `from_currency` | `"USD"` \| `"CAD"` | Yes | Source currency |
| `to_currency` | `"USD"` \| `"CAD"` | Yes | Target currency |
| `date` | `string` | Yes | Date in `YYYY-MM-DD` format |
| `amount` | `number` | No | Amount to convert |

**Example response:**

```
Exchange rate on 2024-01-15: 1 USD = 1.3456 CAD
100 USD = 134.56 CAD
```

> **Note:** Exchange rates are only published on business days. Requests for weekends and Bank of Canada holidays return no data.

## Getting Started

### Prerequisites

- **Python** ≥ 3.12
- **Docker** (for containerised deployment)

### Installation

```bash
git clone https://github.com/bill-ying/mcp-server-py-bank-of-canada-valet.git
cd mcp-server-py-bank-of-canada-valet
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Run Tests

```bash
# Run all tests with coverage report
pytest

# Run a specific test file
pytest tests/domain/test_fx_rate_service.py -v

# Run without coverage (faster for quick iteration)
pytest --no-cov -v
```

### Run Locally

```bash
# Option 1: Via the MCP CLI (stdio transport — for direct MCP client use)
mcp run mcp_server_bank_of_canada.server:mcp

# Option 2: Via uvicorn (SSE transport — for MCP Inspector / AI agents)
uvicorn mcp_server_bank_of_canada.server:app --host 0.0.0.0 --port 7860

# Option 3: Via Docker
docker build -t mcp-server-py-boc .
docker run -p 7860:7860 mcp-server-py-boc
```

The SSE endpoint will be available at `http://localhost:7860/sse`.

## Debugging

### VS Code

This project ships with a `.vscode/launch.json` containing three debug configurations:

| Configuration | Description |
|---|---|
| **MCP Server — uvicorn (SSE)** | Launch the server with `--reload`; set breakpoints in any source file |
| **pytest — all tests** | Run the full test suite in the debugger |
| **pytest — current file** | Debug only the test file open in the editor |

**Steps:**

1. Open the project in VS Code.
2. Set breakpoints in any source file (e.g., `fx_rate_service.py`, `get_rate_tool.py`).
3. Press **F5** and select **MCP Server — uvicorn (SSE)**.
4. Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to send tool calls:

```bash
npx @modelcontextprotocol/inspector
```

5. Connect the Inspector to `http://localhost:7860/sse` and invoke the `get_exchange_rate` tool.

### Docker Debugging

```bash
# Build with OCI labels (version control metadata)
docker build \
  --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  --build-arg GIT_SHA=$(git rev-parse HEAD) \
  -t mcp-server-py-boc:local .

# Run and tail logs
docker run -p 7860:7860 --name boc-debug mcp-server-py-boc:local
docker logs -f boc-debug

# Inspect OCI labels (confirm version traceability)
docker inspect mcp-server-py-boc:local | jq '.[0].Config.Labels'

# Test the SSE endpoint
curl -N http://localhost:7860/sse
```

### Hugging Face Spaces Debugging

```bash
# Stream live build and runtime logs via the HF CLI
pip install huggingface_hub
huggingface-cli login

# Check Space status (building / running / stopped)
hf space info <HF_USERNAME>/<HF_SPACE_NAME>

# Test the live SSE endpoint
curl -N https://<HF_USERNAME>-<HF_SPACE_NAME>.hf.space/sse
```

## CI/CD Pipeline

```
                ┌→ Test (pytest + coverage) ───┐
Push to main ───┤                              ├→ Build & Snyk Scan → Push to Docker Hub → Deploy to HF Spaces
                └──────────────────────────────┘
```

- **Test** and **Build & Snyk Scan** run in parallel.
- **Deploy** runs only after both pass and only on pushes to `main` (not PRs).
- Docker layers are cached via GitHub Actions cache (`type=gha`) to speed up subsequent builds.
- Snyk findings at `high` severity or above **block** deployment (`--severity-threshold=high`).

### GitHub Secrets Setup

Configure these secrets under **Settings → Secrets and variables → Actions**:

| Secret | Description | How to obtain |
|---|---|---|
| `DOCKER_HUB_USERNAME` | Docker Hub username | Your Docker Hub account |
| `DOCKER_HUB_TOKEN` | Docker Hub access token | Docker Hub → Account Settings → Security → New Access Token |
| `SNYK_TOKEN` | Snyk API token | [Snyk Account Settings](https://app.snyk.io/account) |
| `HF_TOKEN` | Hugging Face write-access token | [HF Settings → Access Tokens](https://huggingface.co/settings/tokens) → New token (role: **write**) |
| `HF_USERNAME` | Your Hugging Face username | Your HF profile page |
| `HF_SPACE_NAME` | Name of the target HF Space | The Space you create at [huggingface.co/new-space](https://huggingface.co/new-space) |

### Docker Image Version Control

Each push to `main` produces two Docker tags:

| Tag | Purpose |
|---|---|
| `<sha>` | Immutable, commit-pinned tag for rollback and traceability |
| `latest` | Rolling tag pointing to the most recent build |

Each image also carries [OCI standard labels](https://github.com/opencontainers/image-spec/blob/main/annotations.md):

```bash
# Inspect labels on a pulled image
docker pull <DOCKER_USERNAME>/mcp-server-py-bank-of-canada-valet:<sha>
docker inspect <DOCKER_USERNAME>/mcp-server-py-bank-of-canada-valet:<sha> \
  | jq '.[0].Config.Labels'
```

### Pulling from Docker Hub

```bash
# Latest build
docker pull <DOCKER_USERNAME>/mcp-server-py-bank-of-canada-valet:latest

# Pinned to a specific commit (recommended for production)
docker pull <DOCKER_USERNAME>/mcp-server-py-bank-of-canada-valet:<git-sha>

# Run
docker run -p 7860:7860 <DOCKER_HUB_USERNAME>/mcp-server-py-bank-of-canada-valet:latest
```

## License

This project is licensed under the GPLv3 License.