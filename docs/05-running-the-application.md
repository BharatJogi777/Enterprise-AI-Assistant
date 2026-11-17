# Runbook

## Requirements

Python 3.12+, Docker Compose and Ollama on the host.

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env`: set a unique `API_KEY`. For Tavily search set `TAVILY_API_KEY`. Start PostgreSQL and the API:

```bash
docker compose up -d db
uvicorn enterprise_ai.main:app --reload --app-dir src
```

The host API uses PostgreSQL localhost:5434 and Ollama localhost:11434. Container deployment:

```bash
docker compose up --build
```

The Compose API connects to PostgreSQL by service name and Ollama via host.docker.internal. This is a local development topology, not hardened production deployment.

## API calls

Set the API key in your shell:

```bash
export API_KEY_VALUE='your-local-api-key'
curl http://localhost:8000/api/v1/health/live
curl -H "X-API-Key: $API_KEY_VALUE" -F "file=@./handbook.md" \
  http://localhost:8000/api/v1/documents
curl -H "X-API-Key: $API_KEY_VALUE" -H 'Content-Type: application/json' \
  -d '{"question":"Summarize the leave policy"}' \
  http://localhost:8000/api/v1/assistant/ask
```

Create an agent conversation using a UUID:

```bash
curl -X POST http://localhost:8000/api/v1/conversations/chat \
  -H "X-API-Key: $API_KEY_VALUE" -H 'Content-Type: application/json' \
  -d '{"conversation_id":"9e4a4bd4-68e2-4df1-ae2a-50e9e0a7e4e1","message":"Search our handbook for leave rules and summarize them."}'
```

## MCP

Configure a trusted MCP Streamable HTTP endpoint in `.env`:

```dotenv
MCP_SERVER_URL=http://localhost:9000/mcp
MCP_ALLOWED_TOOLS=lookup_ticket,read_service_health
```

Restart the API. Discover the allowlisted tools at `GET /api/v1/integrations/mcp/tools`, then call a permitted tool through `POST /api/v1/integrations/mcp/call`. Confirm the server's authentication, network policy and tool side effects independently.

## Tests

```bash
python -m pytest -q
ruff check .
```

## Limitations

Only UTF-8 TXT/Markdown is accepted. Chunking is fixed word-window and retrieval is cosine similarity only. Conversation IDs are not bound to authenticated users. The shared API key is not enterprise identity. The DuckDuckGo adapter is an Instant Answer endpoint, not a full web search engine. Langfuse credentials are configuration scaffolding; end-to-end trace export still needs instrumentation and verification. Database tables are currently bootstrapped by application SQL rather than a versioned migration workflow. Do not expose publicly until the controls in docs/07 are completed.
