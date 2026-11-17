# Enterprise AI Assistant

A local-first enterprise AI assistant MVP built with FastAPI, Ollama, PostgreSQL and pgvector. It provides document ingestion, semantic retrieval and grounded question answering.

## Included

- FastAPI application factory and versioned API.
- Liveness and dependency readiness probes.
- Request correlation IDs and JSON structured logs.
- Ollama chat and embedding adapters.
- UTF-8 TXT/Markdown ingestion, overlapping word-window chunking and vector persistence.
- Semantic search and RAG answers with source metadata.
- Optional API-key protection for document and assistant routes.
- Docker Compose for PostgreSQL/pgvector and the API.
- Unit tests for settings and chunking.

## Architecture

```text
Client -> FastAPI -> Document upload -> Chunking -> Ollama embeddings -> PostgreSQL/pgvector
                   -> Question -> Query embedding -> Vector retrieval -> Bounded context
                                                                    -> Ollama chat -> Answer + citations
```

The LLM is not an authorization boundary. The application enforces route access. Retrieved text is untrusted data and must never be interpreted as system instructions.

## Quick start

Requirements: Python 3.12+, Docker Compose, Ollama.

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
docker compose up -d db
uvicorn enterprise_ai.main:app --reload --app-dir src
```

For full container startup, run `docker compose up --build`. The API container connects to Ollama on the host via `host.docker.internal`.

Detailed instructions and curl examples: [docs/05-running-the-application.md](docs/05-running-the-application.md).

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health/live` | Process liveness |
| GET | `/api/v1/health/ready` | PostgreSQL and Ollama readiness |
| POST | `/api/v1/documents` | Ingest TXT/Markdown |
| GET | `/api/v1/documents` | List indexed documents |
| POST | `/api/v1/assistant/search` | Semantic search |
| POST | `/api/v1/assistant/ask` | Grounded question answering |

## Tests

```bash
python -m pytest -q
ruff check .
```

## Important production boundary

This is an executable MVP, not a claim of enterprise production readiness. It does not yet provide enterprise identity/RBAC, tenant isolation, document ACL filtering, rate limiting, audit trails, secret management, migrations, backup/restore, deletion/retention workflows, hybrid retrieval, reranking, external web search, or MCP tool execution. Do not expose it to the public internet until those controls are implemented and tested.

No GitHub Actions workflow is included.
