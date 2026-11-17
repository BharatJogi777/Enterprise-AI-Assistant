# Enterprise AI Assistant

An integrated local-first enterprise assistant built with FastAPI, Ollama, PostgreSQL/pgvector, LangChain, LangGraph and an MCP client. It provides internal-document RAG, optional public-web search, bounded tool-using conversations, persistent conversation history and a two-agent research/synthesis workflow.

## Included

- FastAPI versioned API, CORS, request IDs, JSON logs and liveness/readiness probes.
- TXT/Markdown ingestion, chunking, Ollama embeddings, pgvector retrieval and grounded answers with source metadata.
- Tavily web search adapter and limited DuckDuckGo Instant Answer fallback.
- LangGraph ReAct assistant with server-side allowlisted calculator, UTC, internal-search and web-search tools.
- Two-node LangGraph multi-agent workflow: researcher then synthesizer.
- PostgreSQL conversation history with bounded history retrieval and deletion endpoint.
- MCP Streamable HTTP client with operator-configured endpoint and exact tool-name allowlist.
- Docker Compose, tests, sample evaluation dataset and security/operations docs.

## Quick start

Requirements: Python 3.12+, Docker Compose and Ollama.

```bash
git clone https://github.com/BharatJogi777/Enterprise-AI-Assistant.git
cd Enterprise-AI-Assistant
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
```

Set a unique `API_KEY` in .env. Pull models and start the database:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
docker compose up -d db
uvicorn enterprise_ai.main:app --reload --app-dir src
```

API docs: http://localhost:8000/docs

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health/live` | Process liveness |
| GET | `/api/v1/health/ready` | Database/Ollama readiness |
| POST | `/api/v1/documents` | Ingest TXT/Markdown |
| GET | `/api/v1/documents` | List documents |
| POST | `/api/v1/assistant/search` | Internal semantic search |
| POST | `/api/v1/assistant/ask` | Grounded RAG answer |
| POST | `/api/v1/conversations/chat` | Tool-using agent + memory |
| POST | `/api/v1/conversations/research` | Researcher/synthesizer agents |
| DELETE | `/api/v1/conversations/{uuid}` | Delete conversation messages |
| POST | `/api/v1/integrations/web-search` | Direct web search |
| GET | `/api/v1/integrations/mcp/tools` | List allowlisted MCP tools |
| POST | `/api/v1/integrations/mcp/call` | Call an allowlisted MCP tool |

Protected endpoints require `X-API-Key` when configured. The health probes remain public.

## Integrations

- Web: set `WEB_SEARCH_PROVIDER=tavily` and `TAVILY_API_KEY`. DuckDuckGo Instant Answer is a limited fallback, not a general web index.
- MCP: set `MCP_SERVER_URL` to a trusted Streamable HTTP endpoint and `MCP_ALLOWED_TOOLS` to comma-separated exact tool names. The request body cannot choose a server URL.
- Langfuse: configuration and a small optional client scaffold are present; verify and finish end-to-end trace instrumentation before relying on it operationally.

## Tests

```bash
python -m pytest -q
ruff check .
```

The evaluation starter is in `evals/sample_dataset.json`; see docs/08-evaluation-and-release.md.

## Security boundary

This is a runnable reference implementation, not a certified production system. It still needs enterprise OIDC/RBAC, tenant and document ACL enforcement, conversation ownership, distributed rate limits, audit-grade event logging, managed secrets, formal migrations, backup/restore automation, retention workflows, comprehensive tracing, hybrid retrieval/reranking, advanced file extraction and security/load testing. Do not expose it publicly or ingest confidential company data until those controls are implemented and verified.

See docs/06-integrated-architecture.md and docs/07-security-and-operations.md. No GitHub Actions workflow is included.
