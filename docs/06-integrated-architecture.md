# Integrated architecture

## Runtime topology

```text
Client -> FastAPI -> API-key gate / CORS / request context
                  |-> Document ingestion -> chunking -> Ollama embeddings -> pgvector
                  |-> RAG query -> vector retrieval -> bounded evidence -> Ollama
                  |-> Chat -> LangGraph ReAct -> allowlisted tools -> Ollama
                  |-> Research -> LangGraph researcher -> synthesizer -> answer
                  |-> Integrations -> web provider / configured MCP server
                  |-> Conversation history -> PostgreSQL
                  +-> JSON logs / optional Langfuse integration scaffold
```

## Trust boundaries

The model is an untrusted decision component, never an authorization boundary. Application configuration controls built-in tools and MCP tool allowlists. MCP server URL is operator configuration, not request input. Retrieved documents, web results and tool outputs are untrusted evidence, not instructions. A shared API key is only a local gate; it is not user identity or tenant authorization.

## RAG

UTF-8 TXT/Markdown uploads are byte-limited, split into overlapping word windows, embedded by Ollama, and persisted in PostgreSQL/pgvector. Query vectors retrieve cosine-nearest chunks. Context size is capped before generation. Source metadata is returned with answers. Current retrieval is vector-only; implement hybrid search, metadata filtering, tenant/document ACL predicates and reranking before enterprise use.

## Agents

The single-agent endpoint uses LangGraph's prebuilt ReAct graph with a recursion limit. The multi-agent endpoint is a sequential researcher -> synthesizer graph. The researcher can use allowlisted internal/web search; the synthesizer is instructed to answer only from collected evidence. These are bounded workflows, not autonomous agents with unrestricted access.

## MCP and web

MCP uses Streamable HTTP and one operator-configured server URL with an exact tool allowlist. Web search supports Tavily and a limited DuckDuckGo Instant Answer fallback. Use a provider with clear quotas, attribution and data-retention terms for production.
