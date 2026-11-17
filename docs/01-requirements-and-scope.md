# 01 — Product Requirements and Scope

## 1. Purpose

Build an enterprise-oriented assistant that combines language-model generation with controlled access to private documents, web search, and approved operational tools.

The application is not simply a chat interface around an LLM. It is a backend system that must manage identity, data boundaries, retrieval, orchestration, tool permissions, evaluation, observability, and failure handling.

## 2. Users and primary use cases

### User roles

- **User:** asks questions and accesses resources they are authorized to use.
- **Administrator:** manages application configuration, users, document collections, and tool permissions.
- **Operator/developer:** diagnoses service health, traces, model behavior, and evaluation failures.

Authentication and role management will be introduced before exposing the service beyond a trusted local environment.

### Use case A — Document question answering

1. An administrator or authorized user uploads a supported document.
2. The ingestion pipeline validates type and size.
3. Text is extracted and normalized.
4. Text is split into traceable chunks.
5. An embedding model converts chunks into vectors.
6. Chunks and metadata are stored in PostgreSQL with pgvector.
7. A user asks a question.
8. The retrieval service finds relevant chunks within the user's authorized scope.
9. The model receives the question and selected evidence.
10. The API returns an answer and source references.

**Acceptance criteria**
- Every returned source points to a stored document and chunk.
- A response must not fabricate source IDs, page numbers, or quotations.
- If evidence is insufficient, the assistant says so instead of guessing.
- Retrieval respects collection and document authorization.
- The system records retrieval and generation metadata without logging secrets.

### Use case B — Controlled web search

1. The user asks a question that needs current external information.
2. The orchestration layer determines whether web search is needed.
3. A search adapter calls a configured provider.
4. Results are normalized into a common schema.
5. The model receives bounded snippets and source URLs.
6. The response distinguishes external sources from internal documents.

**Acceptance criteria**
- Search is performed only through an explicitly configured provider.
- Provider errors and empty results are represented honestly.
- URLs and source metadata are preserved.
- Search result content is treated as untrusted input.
- The model cannot interpret webpage instructions as system or developer instructions.

The first implementation will use a provider interface and a mock adapter for deterministic tests. A real provider adapter will be added later after provider and cost constraints are confirmed.

### Use case C — Approved tool execution

1. The assistant identifies a possible tool action.
2. The application checks whether the tool is registered and permitted.
3. Arguments are validated against a strict schema.
4. Authorization and risk policy are checked outside the model.
5. The tool is invoked with a timeout and bounded retries.
6. The result is normalized and returned to the model.
7. The final response accurately reports what happened.

**Acceptance criteria**
- The model cannot grant itself permissions.
- Tool names and arguments are validated server-side.
- Mutating actions require explicit policy; high-impact actions may require human approval.
- Tool calls have timeouts, audit metadata, and bounded output sizes.
- Retries do not duplicate non-idempotent actions.
- An unavailable tool is never represented as a successful action.

### Use case D — Multi-step investigation

The assistant can perform a bounded workflow such as: search approved knowledge sources, inspect relevant records using read-only tools, compare evidence, and produce a cited report.

**Acceptance criteria**
- The workflow has a maximum step count and execution deadline.
- State transitions are explicit and inspectable.
- Each tool call is independently authorized.
- The workflow can stop safely on missing evidence, denied permissions, or repeated errors.
- The report distinguishes evidence, inference, and unknowns.

## 3. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Expose health and readiness endpoints | P0 |
| FR-02 | Accept chat requests through a versioned API | P0 |
| FR-03 | Call a configured Ollama model | P0 |
| FR-04 | Ingest documents and preserve metadata | P1 |
| FR-05 | Chunk, embed, and store document content | P1 |
| FR-06 | Retrieve relevant chunks with authorization filters | P1 |
| FR-07 | Return answers with source citations | P1 |
| FR-08 | Support a provider-neutral web-search interface | P2 |
| FR-09 | Register and validate approved tools | P2 |
| FR-10 | Connect to MCP servers through a controlled client | P2 |
| FR-11 | Run bounded multi-step workflows | P2 |
| FR-12 | Record traces and operational metrics | P1 |
| FR-13 | Evaluate prompts, retrieval, and agent behavior | P1 |
| FR-14 | Apply release gates to evaluation results | P2 |
| FR-15 | Add authentication and role-based authorization | P1 before external exposure |

Priorities describe implementation order, not permission to expose an incomplete system publicly.

## 4. Non-functional requirements

### Reliability
- External calls have explicit timeouts.
- Retries are bounded and use backoff where appropriate.
- Database transactions protect related writes.
- Readiness reflects required dependencies; liveness does not fail merely because an optional provider is unavailable.
- Failures return stable error responses with correlation IDs.

### Performance
- Establish a baseline before optimizing.
- Measure API latency separately from model latency, embedding latency, retrieval latency, and tool latency.
- Limit prompt size, retrieved context, output tokens, and concurrent model requests.
- Avoid assuming that local hardware can support high concurrency.

### Security and privacy
- Secrets are supplied through environment variables or a secret manager, never committed.
- Uploaded files are validated and size-limited.
- Document access is checked at retrieval time, not just upload time.
- Tool authorization is enforced by application code.
- Retrieved documents and web content are untrusted data.
- Logs avoid raw secrets and unnecessary personal or document content.
- Destructive tools are disabled by default.

### Maintainability
- Separate API, domain, orchestration, infrastructure, and provider adapters.
- Use typed request/response schemas.
- Keep business logic out of route handlers.
- Make model, embedding, database, and search providers replaceable.
- Pin dependencies and test upgrades.

### Testability
- Unit tests must not require Ollama, PostgreSQL, or network access.
- Integration tests use explicitly configured dependencies.
- LLM-dependent tests use a deterministic fake model by default.
- A smaller optional smoke-test suite validates the local Ollama integration.

## 5. Scope boundaries and assumptions

- The first target is a single-developer local environment.
- The initial inference runtime is Ollama.
- The initial relational and vector store is PostgreSQL with pgvector.
- The first version is not a high-availability distributed deployment.
- Model outputs are probabilistic; correctness is measured with datasets and assertions, not assumed.
- The assistant is advisory. It must not perform consequential actions without an explicit authorization and approval design.

## 6. Release acceptance checklist

A release candidate is not complete until:
- [ ] API schemas and error behavior are documented.
- [ ] Authorization is enforced for every protected resource.
- [ ] No secrets are committed.
- [ ] Unit tests pass.
- [ ] Relevant integration tests pass.
- [ ] RAG answers are evaluated against a versioned dataset.
- [ ] Citation validity is measured.
- [ ] Tool authorization and failure cases are tested.
- [ ] Latency and resource usage are measured.
- [ ] Logs and traces do not expose sensitive payloads.
- [ ] Deployment and rollback steps are documented.
