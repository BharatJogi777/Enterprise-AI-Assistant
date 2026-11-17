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

Edit `.env` and set a unique `API_KEY`. For Tavily search, set `TAVILY_API_KEY`. Start PostgreSQL and API:

```bash
docker compose up -d db
uvicorn enterprise_ai.main:app --reload --app-dir src
```

The host API uses PostgreSQL localhost:5434 and Ollama localhost:11434. For containerized API, run `docker compose up --build`; it connects to PostgreSQL by service name and Ollama via host.docker.internal. This is a developer topology, not a hardened production deployment.

## API calls

```bash
export API_KEY_VALUE='your-local-api-key'
curl http://localhost:8000/api/v1/health/live
curl -H "X-API-Key: $API_KEY_VALUE" -F "file=@./handbook.md" \
  http://localhost:8000/api/v1/documents
curl -H "X-API-Key: $API_KEY_VALUE" -H 'Content-Type: application/json' \
  -d '{"question":"Summarize the leave policy"}' \
  http://localhost:8000/api/v1/assistant/ask
```

Agent conversation:

```bash
curl -X POST http://localhost:8000/api/v1/conversations/chat \
  -H "X-API-Key: $API_KEY_VALUE" -H 'Content-Type: application/json' \
  -d '{"conversation_id":"9e4a4bd4-68e2-4df1-ae2a-50e9e0a7e4e1","message":"Search our handbook for leave rules and summarize them."}'
```

Multi-agent researcher/synthesizer workflow uses the same request body at `POST /api/v1/conversations/research`.

## Multiple MCP servers

Configure only trusted Streamable HTTP servers. The value is JSON; each server has a unique name, URL and exact allowlist:

```dotenv
MCP_SERVERS_JSON=[{"name":"tickets","url":"http://host.docker.internal:9001/mcp","allowed_tools":["lookup_ticket","create_ticket"]},{"name":"monitoring","url":"http://host.docker.internal:9002/mcp","allowed_tools":["read_service_health"]}]
```

In a dotenv file, quote the JSON value if your shell/parser requires it. Restart the API. Discover allowlisted tools at `GET /api/v1/integrations/mcp/tools`. Call a permitted tool using `POST /api/v1/integrations/mcp/call` with `server_name`, `tool_name` and `arguments`. Verify each server's authentication, network policy and side effects independently.

## Tests

```bash
python -m pytest -q
ruff check .
```

## Limitations

Only UTF-8 TXT/Markdown is accepted. Chunking is fixed word-window and retrieval is cosine similarity only. Conversation IDs are not bound to authenticated users. The shared API key is not enterprise identity. DuckDuckGo Instant Answer is not a full web search engine. Langfuse configuration exists but end-to-end trace export still requires instrumentation and verification. Database tables are bootstrapped by application SQL rather than a versioned migration workflow. Do not expose publicly until the controls in docs/07 are completed.
