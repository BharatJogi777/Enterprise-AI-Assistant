# 02 — System Architecture

## 1. Architectural style

Use a modular monolith for the first release.

A modular monolith is one deployable backend with clear internal boundaries. It avoids premature microservice complexity while allowing components to be extracted later if measured scaling or isolation requirements justify it.

The API process owns request validation, authorization, orchestration, and response construction. Model inference, database persistence, and MCP tool execution remain behind explicit adapters.

## 2. Logical architecture

~~~mermaid
flowchart TB
    Client[Web UI / API Client] --> API[FastAPI API Layer]
    API --> Auth[Authentication and Authorization]
    API --> App[Application Use Cases]
    App --> Router[Assistant Orchestrator]
    Router --> Prompt[Prompt Registry]
    Router --> LLM[LLM Adapter]
    Router --> RAG[RAG Service]
    Router --> Search[Web Search Adapter]
    Router --> Tools[Tool Policy and Registry]
    LLM --> Ollama[Ollama Runtime]
    RAG --> Embed[Embedding Adapter]
    RAG --> DB[(PostgreSQL + pgvector)]
    Search --> Provider[Search Provider]
    Tools --> MCP[MCP Client]
    MCP --> Servers[Approved MCP Servers]
    API --> Telemetry[Tracing / Metrics / Logs]
    App --> Telemetry
    Router --> Telemetry
~~~

The diagram describes logical boundaries, not a promise that every component will run as a separate process.

## 3. Main components and responsibilities

### API layer

Responsibilities:
- Parse and validate HTTP requests.
- Apply authentication dependencies.
- Map application results to response schemas.
- Convert known application errors into stable HTTP responses.
- Propagate request and correlation IDs.

Must not:
- Build prompts inline in route handlers.
- Directly execute arbitrary tools.
- Contain vector-search SQL or model-provider details.

### Application/use-case layer

Coordinates user-facing operations such as AskAssistant, IngestDocument, and RunInvestigation.

It owns the sequence of domain operations and transaction boundaries. It should depend on interfaces rather than concrete Ollama or database clients.

### Assistant orchestrator

Coordinates model calls and optional retrieval/tool steps.

It enforces:
- Maximum model/tool steps.
- Overall deadline and per-call timeout.
- Context and output limits.
- Tool allow-list and policy checks.
- Stop conditions and error propagation.

LangChain is an orchestration library, not the security boundary. Application code must enforce permissions regardless of model or framework behavior.

### Prompt registry

Stores named, versioned prompt templates and metadata.

A prompt release should identify:
- Prompt name and version.
- Required variables.
- Intended task.
- Model assumptions.
- Evaluation dataset version.
- Change notes.

A prompt change must be evaluated against a baseline before activation.

### LLM adapter

Provides a provider-neutral interface for:
- Chat completion.
- Structured output where supported.
- Model metadata and usage extraction.
- Timeouts and normalized provider errors.

The initial adapter calls Ollama. The domain layer should not depend on Ollama-specific response objects.

### RAG service

Responsibilities:
1. Document extraction and normalization.
2. Chunking with stable chunk identity.
3. Embedding generation.
4. Persistence of document, chunk, and embedding metadata.
5. Authorization-aware retrieval.
6. Optional reranking.
7. Context assembly with token/character budgets.
8. Citation construction and validation.

The first retrieval implementation can use pgvector similarity search. Hybrid search and reranking should be added only after evaluation demonstrates a need.

### Search adapter

Defines a provider-neutral interface for web search. Provider credentials and HTTP details remain in infrastructure code. Search content is untrusted and must be bounded before it enters a prompt.

### Tool registry and MCP client

The tool registry describes available tools and their schemas. The policy layer checks user permissions and action risk before execution. MCP is a transport/protocol integration, not an authorization system.

Initial policy:
- Read-only tools may be enabled selectively.
- Mutating tools are disabled by default.
- Destructive or external side-effect tools require explicit approval design.
- Tool descriptions and results are untrusted data.

### Persistence

PostgreSQL is the source of truth for application metadata and document records. pgvector stores embeddings alongside chunk metadata.

Expected conceptual entities:
- users
- document_collections
- documents
- document_chunks
- conversations
- messages
- prompt_versions
- tool_audit_events
- evaluation_runs

Exact schemas and migrations will be designed in the database implementation phase.

### Observability

Each request should have a correlation/trace identifier and capture safe metadata for:
- API route and status.
- Model and prompt version.
- Retrieval duration and result count.
- Tool names, duration, and outcome.
- Token usage when available.
- Total latency and error category.

Do not indiscriminately log full prompts, uploaded content, credentials, or tool payloads. Observability should be useful without becoming a data leak.

## 4. Request flow — document question answering

~~~mermaid
sequenceDiagram
    participant U as User
    participant A as FastAPI
    participant P as Policy/Auth
    participant R as RAG Service
    participant D as PostgreSQL/pgvector
    participant M as Ollama
    U->>A: POST /api/v1/assistant/ask
    A->>P: Authenticate and authorize
    P-->>A: Authorized identity and scope
    A->>R: Retrieve(question, scope)
    R->>D: Similarity search with scope filters
    D-->>R: Ranked chunks and metadata
    R-->>A: Evidence bundle
    A->>M: Generate(answer prompt + bounded evidence)
    M-->>A: Model response
    A->>A: Validate citation references
    A-->>U: Answer + verified source metadata
~~~

Citation validation verifies that cited identifiers exist in the evidence bundle. It cannot prove every natural-language claim is entailed by a citation; that requires separate evaluation and potentially human review.

## 5. Request flow — tool calling

1. The model proposes a tool name and arguments.
2. The orchestrator checks the registered tool.
3. JSON/schema validation runs.
4. Authorization checks the current principal and requested action.
5. Risk policy determines whether approval is required.
6. The MCP client calls the configured server.
7. The result is normalized, size-limited, and added as tool output.
8. The model may continue only within the workflow's remaining step budget.

The model proposal is never treated as authorization.

## 6. State and execution limits

Every request/workflow should carry:
- Request ID.
- Authenticated principal.
- Start time and deadline.
- Current step count and maximum step count.
- Model-call count and maximum model-call count.
- Tool-call count and maximum tool-call count.
- Token/context budget.
- Cancellation state.

Use bounded execution. A loop that continues until the model says it is finished is not a production-safe control strategy.

## 7. Failure handling

| Failure | Expected behavior |
|---|---|
| Ollama unavailable | Return controlled dependency error; do not fabricate an answer |
| Database unavailable | Fail readiness; return controlled service error |
| Embedding model unavailable | Ingestion fails visibly; do not store incomplete vectors |
| No relevant evidence | Explain insufficient evidence or use an explicitly permitted fallback |
| Search provider timeout | Return partial result only if policy allows; disclose search failure |
| MCP server unavailable | Mark tool unavailable; do not claim execution |
| Invalid tool arguments | Reject before invocation |
| Permission denied | Stop the action and record safe audit metadata |
| Deadline exceeded | Cancel remaining work where possible and return timeout |
| Invalid citation ID | Remove invalid citation or fail validation; never emit fabricated source |

## 8. Deployment topology

### Local development

- FastAPI runs in a Python environment or container.
- PostgreSQL + pgvector runs in Docker Compose.
- Ollama runs on the host initially, avoiding memory overhead of running it inside Docker on a small machine.
- Langfuse may be configured as a hosted service or a later self-hosted deployment.
- MCP servers are started explicitly and configured by allow-list.

### Future production topology

Only after requirements and load tests justify it:
- Multiple stateless API replicas.
- Managed PostgreSQL with backups and connection pooling.
- Dedicated worker process for ingestion.
- Centralized secrets and identity provider.
- Rate limiting and request quotas.
- Centralized telemetry and alerting.
- Model serving scaled independently from API workers.

Do not split the first version into microservices without a measured reason.

## 9. Architecture decisions to preserve

- The model does not own permissions.
- Retrieval must be scoped to the authenticated principal.
- Every external dependency is behind an adapter.
- All agent loops are bounded by application-controlled limits.
- Prompt and model versions are recorded for reproducibility.
- Quality changes require evaluation, not subjective spot-checking alone.
