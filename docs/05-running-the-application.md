# Runbook

## Requirements

- Python 3.12+
- Docker Desktop / Docker Compose
- Ollama running on the host

Pull the configured models:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

## Local development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
docker compose up -d db
uvicorn enterprise_ai.main:app --reload --app-dir src
```

Local API connects to PostgreSQL on localhost:5434 and Ollama on localhost:11434.

## Compose

```bash
cp .env.example .env
docker compose up --build
```

The Compose API uses the internal database hostname and reaches Ollama at host.docker.internal. This is a developer topology, not a hardened production deployment.

## API usage

```bash
curl http://localhost:8000/api/v1/health/live

curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@./handbook.md"

curl -X POST http://localhost:8000/api/v1/assistant/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"leave policy","top_k":5}'

curl -X POST http://localhost:8000/api/v1/assistant/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"How many days of annual leave are provided?"}'
```

Set a non-empty `API_KEY` in .env to require `X-API-Key` on document and assistant routes. The health probes remain unauthenticated.

## Tests

```bash
python -m pytest -q
ruff check .
```

## Current limitations

Only UTF-8 TXT and Markdown uploads are accepted. Chunking is fixed-size word-window; retrieval is vector cosine similarity only. There is no reranker, hybrid search, tenant/document ACL enforcement, document deletion, enterprise identity provider, external search integration, or MCP execution yet. Before public exposure add threat modeling, identity/RBAC, tenant isolation, ACL-aware retrieval, rate limiting, audit logging, secret management, schema migrations, backups, retention/deletion workflows, observability, and security/load testing.
