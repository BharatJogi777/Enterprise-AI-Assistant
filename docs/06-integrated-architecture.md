# Integrated architecture

## Runtime topology

```text
Clients
  |
  v
FastAPI /api/v1 -- request ID, CORS, API-key gate
  |-- Documents --> extraction boundary --> chunking --> Ollama embeddings
  |                                                   --> PostgreSQL + pgvector
  |-- Assistant search/ask --> query embedding --> cosine retrieval
  |                                            --> bounded evidence context
  |                                            --> Ollama chat
  |-- Conversations --> PostgreSQL history --> LangGraph ReAct agent
  |                                          |--> calculator / UTC clock
  |                                          |--> internal document search
  |                                          |--> bounded Ollama tool loop
  |-- Integrations --> web search provider adapter
                     --> configured MCP Streamable HTTP server
  |
  +--> JSON logs / request IDs / optional Langfuse client
```

## Trust boundaries

- The model is an untrusted decision component. It does not grant permissions.
- Tool availability is constrained by server-side allowlists.
- MCP server URL is operator configuration, never a user-supplied URL.
- MCP tool names are separately allowlisted. Only connect to servers you administer or trust.
- Retrieved documents, web results, and tool outputs are untrusted data; prompts explicitly say not to follow instructions embedded in evidence.
- API key is a shared local gate, not enterprise identity. Use an identity-aware gateway and per-user authorization before multi-user deployment.
- Conversation IDs are identifiers, not authorization. Add ownership checks before enabling multi-user use.

## RAG pipeline

1. Accept UTF-8 TXT/Markdown only and enforce byte limits.
2. Split into overlapping word windows.
3. Request embeddings from Ollama and validate dimensions.
4. Persist documents/chunks in PostgreSQL with pgvector.
5. Embed query and rank by cosine distance.
6. Cap retrieved context characters.
7. Ask Ollama to answer only from evidence and return source metadata.

Current retrieval is vector-only. Add hybrid BM25/vector retrieval, metadata filters, tenant/document ACL predicates and reranking before high-stakes use.

## Agent workflow

The LangGraph prebuilt ReAct graph alternates model decisions and allowlisted tools. A recursion limit bounds graph execution. It is not a guarantee of a fixed wall-clock SLA; add request deadlines, per-tool timeouts and a central execution budget for production.

## MCP

The MCP adapter uses Streamable HTTP. Configure one trusted server URL and explicit tool-name allowlist. For multiple servers, deploy a gateway or extend configuration to named server records with per-server tool allowlists, credentials and timeouts. Never blindly expose every discovered MCP tool to the model.

## Web search

Tavily is supported as a provider with an API key. The DuckDuckGo Instant Answer endpoint is a limited fallback and is not equivalent to a full search index. For production, prefer a provider with stable search-result coverage, quotas, attribution and documented retention controls.
