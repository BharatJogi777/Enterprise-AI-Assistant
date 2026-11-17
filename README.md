# Enterprise AI Assistant

An integrated, local-first enterprise assistant built around FastAPI, Ollama, PostgreSQL/pgvector, LangChain and LangGraph. It combines internal-document RAG, optional public-web search, bounded tool-using conversations, persistent conversation history and an explicitly configured MCP client.

## Features in this repository

- **API foundation:** FastAPI app factory, versioned routes, CORS configuration, request IDs, JSON logs and liveness/readiness probes.
- **RAG:** UTF-8 TXT/Markdown ingestion, overlapping chunking, Ollama embeddings, pgvector cosine retrieval, bounded context and source metadata.
- **Web search:** Tavily adapter; DuckDuckGo Instant Answer fallback (limited coverage, not a full search index).
- **Agent:** LangGraph ReAct workflow using Ollama with an explicit server-side tool allowlist (calculator, UTC clock, internal search and web search).
- **Memory:** PostgreSQL conversation history with bounded history retrieval and conversation deletion endpoint.
- **MCP:** Streamable HTTP client with operator-configured server URL and explicit remote-tool allowlist.
- **Operations:** Docker Compose, health probes, environment configuration, unit tests, evaluation starter dataset and security/release documentation.

## Architecture

```text
Client -> FastAPI -> API-key gate / request context
                  |-> Documents -> chunk -> Ollama embeddings -> PostgreSQL/pgvector
                  |-> RAG ask -> retrieve -> bounded evidence -> Ollama response
                  |-> Chat -> LangGraph -> allowlisted tools -> Ollama
                  |                         |-> internal RAG
                  |                         |-> public web search
                  |                         |-> calculator / UTC clock
                  |-> Integrations -> web provider / configured MCP server
                  |-> Conversations -> PostgreSQL message history
```

The model is not an authorization boundary. Tool permissions are enforced by application configuration. Documents, web results and tool outputs are untrusted evidence, not instructions.

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

Set a unique local API key in `.env`. Pull models and start services:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
docker compose up -d db
uvicorn enterprise_ai.main:app --reload --app-dir src
```

Open http://localhost:8000/docs. For the containerized API, run `docker compose up --build`; Ollama remains on the host and is reached through `host.docker.internal`.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health/live` | Process liveness |
| GET | `/api/v1/health/ready` | PostgreSQL + Ollama connectivity |
| POST | `/api/v1/documents` | Upload TXT/Markdown |
| GET | `/api/v1/documents` | List indexed documents |
| POST | `/api/v1/assistant/search` | Semantic internal search |
| POST | `/api/v1/assistant/ask` | Grounded RAG answer |
| POST | `/api/v1/conversations/chat` | LangGraph agent conversation |
| DELETE | `/api/v1/conversations/{uuid}` | Delete conversation history |
| POST | `/api/v1/integrations/web-search` | Direct public web search |
| GET | `/api/v1/integrations/mcp/tools` | Discover allowlisted MCP tools |
| POST | `/api/v1/integrations/mcp/call` | Call an allowlisted MCP tool |

Protected endpoints require `X-API-Key` when `API_KEY` is configured. The example environment sets a placeholder; replace it before use.

## Web search configuration

Recommended: set `WEB_SEARCH_PROVIDER=tavily` and provide `TAVILY_API_KEY`. The default sample configuration uses Tavily. DuckDuckGo Instant Answer can be selected for a keyless but limited fallback. Public web search sends the user's query to the configured provider.

## MCP configuration

Set `MCP_SERVER_URL` to a trusted Streamable HTTP MCP server and `MCP_ALLOWED_TOOLS` to comma-separated exact tool names. The API never accepts a server URL from a request. Do not expose arbitrary MCP servers or discovered tools to end users.

## Tests and evaluation

```bash
python -m pytest -q
ruff check .
python -c "import asyncio; from enterprise_ai.evaluation.runner import evaluate_dataset; print(asyncio.run(evaluate_dataset('evals/sample_dataset.json')))"
```

The sample evaluation data is illustrative. Add a reviewed gold dataset before using scores as release gates.

## Documentation

- [Requirements and scope](docs/01-requirements-and-scope.md)
- [Initial architecture](docs/02-system-architecture.md)
- [Technology decisions](docs/03-technology-decisions.md)
- [Implementation roadmap](docs/04-implementation-roadmap.md)
- [Runbook](docs/05-running-the-application.md)
- [Integrated architecture](docs/06-integrated-architecture.md)
- [Security and operations](docs/07-security-and-operations.md)
- [Evaluation and release gates](docs/08-evaluation-and-release.md)

## Explicit limitations

This is a substantial runnable reference implementation, not a certified production system. It currently supports TXT/Markdown only; vector-only retrieval; a shared API key rather than enterprise OIDC/RBAC; conversation IDs without user ownership; one configured MCP server; basic web-search integration; and starter evaluation. It does not yet include tenant/document ACL isolation, PDF/DOCX/OCR, hybrid retrieval/reranking, admin UI, audit-grade events, distributed rate limits, managed secrets, formal schema migration automation, backup/restore automation, or comprehensive tracing. Do not expose it publicly or load confidential enterprise data until the security and operational controls in the documentation are implemented and tested.

No GitHub Actions workflow is included.
