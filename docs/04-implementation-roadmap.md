# 04 — Implementation Roadmap

The project is implemented in small, verifiable phases. Each phase should leave the repository in a coherent state.

## Phase 1 — Requirements and architecture

**Status:** Documentation baseline created.

Deliverables:
- Product requirements and acceptance criteria.
- Logical architecture and request flows.
- Technology decisions and trade-offs.
- Implementation roadmap and repository conventions.

Exit criteria:
- Scope and non-goals are clear.
- Component responsibilities and security boundaries are documented.
- Implementation order is agreed.

## Phase 2 — Python application foundation

Deliverables:
- Production-oriented source layout.
- Dependency and configuration management.
- Pydantic settings and environment validation.
- FastAPI application factory.
- Versioned API router.
- Liveness and readiness endpoints.
- Structured logging and correlation IDs.
- Unit tests and local run instructions.

Exit criteria:
- API starts with validated configuration.
- Liveness does not depend on optional services.
- Readiness reports required dependency state.
- Tests run without Ollama or PostgreSQL.

## Phase 3 — Ollama model adapter

Deliverables:
- Provider interface.
- Ollama chat adapter.
- Timeouts and normalized errors.
- Model configuration and health checks.
- Fake adapter for unit tests.
- Optional local model smoke test.

Exit criteria:
- API can call the configured local model.
- Provider response is normalized.
- Failure and timeout behavior are tested.

## Phase 4 — PostgreSQL and persistence foundation

Deliverables:
- Docker Compose PostgreSQL + pgvector.
- Database connection lifecycle.
- Migration tooling.
- Initial schema and repositories.
- Transaction boundaries and integration tests.

Exit criteria:
- Schema can be created from migrations.
- Repository operations are tested.
- Connection failure is surfaced clearly.

## Phase 5 — Document ingestion pipeline

Deliverables:
- Upload API and validation.
- File type and size limits.
- Text extraction adapters.
- Normalization and chunking.
- Stable document/chunk metadata.
- Ingestion status and failure handling.

Exit criteria:
- Supported sample documents can be ingested.
- Invalid files are rejected.
- Chunk provenance is preserved.

## Phase 6 — Embeddings and vector retrieval

Deliverables:
- Embedding adapter (initially Ollama).
- Embedding model/dimension configuration.
- pgvector persistence and indexes.
- Similarity search.
- Authorization-aware metadata filters.
- Retrieval evaluation dataset and metrics.

Exit criteria:
- Search returns ranked chunks.
- Unauthorized chunks cannot be retrieved.
- Recall and ranking can be measured.

## Phase 7 — Grounded RAG answering

Deliverables:
- Context assembly and budget controls.
- Versioned RAG prompt.
- Answer generation.
- Citation construction and validation.
- Insufficient-evidence behavior.
- RAG evaluation runner.

Exit criteria:
- Answers return source metadata.
- Unknown questions do not trigger fabricated citations.
- Evaluation includes retrieval and answer quality.

## Phase 8 — Prompt registry and optimization

Deliverables:
- Immutable prompt versions.
- Variable/schema validation.
- Environment activation.
- Prompt experiment datasets.
- Baseline comparison and release gate.

Exit criteria:
- Every answer trace identifies the prompt version.
- Prompt changes can be compared reproducibly.
- Regressions block promotion.

## Phase 9 — Web search integration

Deliverables:
- Provider-neutral search interface.
- Deterministic mock provider.
- Configured real provider adapter.
- Source normalization and URL validation.
- Search timeout, error, and content limits.
- Prompt-injection handling for retrieved web content.

Exit criteria:
- Search provider can be replaced without changing domain logic.
- Failures are disclosed.
- Web content cannot override system policy.

## Phase 10 — Tool registry and MCP integration

Deliverables:
- Tool schemas and registry.
- Authorization policy.
- MCP client lifecycle and server configuration.
- Read-only sample MCP server.
- Tool timeout and output limits.
- Audit events and failure tests.

Exit criteria:
- Only registered and authorized tools execute.
- Invalid arguments are rejected before invocation.
- Mutating tools remain disabled until approval policy exists.

## Phase 11 — Bounded agent workflows

Deliverables:
- Explicit workflow state.
- LangGraph workflow where justified.
- Step, time, model-call, and tool-call budgets.
- Retry and idempotency strategy.
- Human approval checkpoint design.
- Agent evaluation dataset.

Exit criteria:
- Workflow cannot run indefinitely.
- Every tool call is policy-checked.
- Partial failures are represented honestly.

## Phase 12 — Observability and operations

Deliverables:
- Langfuse integration.
- Safe trace metadata.
- Metrics and dashboards guidance.
- Dependency health and structured errors.
- Privacy and retention settings.
- Troubleshooting runbook.

Exit criteria:
- A request can be traced across retrieval, generation, and tools.
- Sensitive payloads are not logged by default.
- Telemetry failure behavior is documented.

## Phase 13 — Authentication and authorization hardening

Deliverables:
- Authentication strategy.
- User and role model.
- Collection/document access policy.
- Tool permissions.
- Rate limits and request quotas.
- Security tests and threat review.

Exit criteria:
- Every protected operation checks identity and permission.
- Retrieval cannot cross user/tenant boundaries.
- Secrets and sensitive data are handled safely.

## Phase 14 — End-to-end evaluation and release

Deliverables:
- Versioned test datasets.
- RAG and agent quality metrics.
- Latency and resource measurements.
- Regression thresholds and release gate.
- Reproducible evaluation reports.
- Deployment, backup, and rollback guidance.

Exit criteria:
- A candidate can be evaluated against a baseline.
- Critical safety failures block release.
- Known limitations and measured performance are documented.

## Phase 15 — Production readiness review

Deliverables:
- Deployment topology decision.
- Capacity and load test plan.
- Backup/restore validation.
- Alerting and incident runbooks.
- Dependency update process.
- Security review and release checklist.

Exit criteria:
- Operational owner and recovery procedures are defined.
- Load and failure behavior are measured.
- No unsupported production-readiness claims remain.

## Working agreement for each phase

Each phase will follow this sequence:

1. Explain the concept and the problem it solves.
2. Show the architecture and request/data flow.
3. Add files in a deliberate order.
4. Explain important code paths and trade-offs.
5. Add tests before declaring the phase complete.
6. Provide commands to run locally.
7. Document expected output and troubleshooting.
8. Commit the finished work.

Do not skip directly to agents before the API, model adapter, persistence, retrieval, and evaluation foundations are understood.
