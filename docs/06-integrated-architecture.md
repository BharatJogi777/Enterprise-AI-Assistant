# Integrated architecture

## Runtime topology

```text
Client -> FastAPI -> API-key gate / CORS / request context
                  |-> Documents -> chunking -> Ollama embeddings -> pgvector
                  |-> RAG query -> vector retrieval -> bounded evidence -> Ollama
                  |-> Chat -> LangGraph ReAct -> allowlisted tools
                  |-> Research -> researcher agent -> synthesis agent
                  |-> Integrations -> web provider / named MCP servers
                  |-> Conversation history -> PostgreSQL
                  +-> JSON logs / optional Langfuse integration scaffold
```

## Trust boundaries

The model is not an authorization boundary. Application configuration controls built-in tools and per-server MCP tool allowlists. MCP server URLs are operator-supplied JSON configuration, never request input. Retrieved documents, web results and tool outputs are untrusted evidence, not instructions. A shared API key is only a local gate; it is not user identity or tenant authorization.

## RAG

UTF-8 TXT/Markdown uploads are byte-limited, split into overlapping word windows, embedded by Ollama, and persisted in PostgreSQL/pgvector. Query vectors retrieve cosine-nearest chunks. Context size is capped before generation. Source metadata is returned with answers. Current retrieval is vector-only; implement hybrid search, metadata filtering, tenant/document ACL predicates and reranking before enterprise use.

## Agents

The single-agent endpoint uses LangGraph's prebuilt ReAct graph with a recursion limit. The multi-agent endpoint is a sequential researcher -> synthesizer graph. The researcher can use allowlisted internal/web search; the synthesizer answers from the evidence bundle. These are bounded workflows, not autonomous agents with unrestricted access.

## MCP and web

MCP uses Streamable HTTP. Configure multiple trusted servers in `MCP_SERVERS_JSON`, each with a unique `name`, `url` and exact `allowed_tools` array. The API never accepts server URLs or unlisted tool names from clients. Web search supports Tavily and a limited DuckDuckGo Instant Answer fallback.
