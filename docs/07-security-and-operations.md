# Security and operations checklist

## Required before production

- Replace the shared API key with OIDC/OAuth2 authentication and user/tenant authorization.
- Enforce tenant and document ACL filters inside every retrieval query; do not rely on prompt instructions.
- Bind conversation records to authenticated owners and enforce ownership on reads/deletes.
- Put API behind TLS termination, request-size limits, rate limiting and a WAF/API gateway.
- Store secrets in a secret manager; rotate provider keys.
- Restrict outbound network egress. MCP servers must be explicitly trusted and allowlisted.
- Add audit events for document access, tool invocation, admin changes and data deletion.
- Add retention, export and verified deletion workflows for documents, embeddings and conversation history.
- Use versioned database migrations, backups, restore drills and connection pooling.
- Add per-request deadlines, provider retries with jitter, circuit breakers and concurrency limits.
- Add dependency scanning, SBOM, SAST, DAST, penetration testing and load testing.
- Review data residency, model/provider data handling and employee acceptable-use policies.

## Current implementation controls

- File byte limit and TXT/Markdown extension allowlist.
- Embedding dimensions validated before persistence.
- Context character cap for RAG.
- Arithmetic evaluator uses an AST allowlist, not eval/exec.
- MCP URL is operator-configured and tool names are allowlisted.
- API key comparison uses constant-time comparison.
- Request IDs are validated and echoed.
- CORS origins are configurable.
- Agent graph recursion is bounded.

## Operational probes

- `GET /api/v1/health/live`: process liveness only.
- `GET /api/v1/health/ready`: checks PostgreSQL connectivity and Ollama HTTP availability.

Readiness currently does not verify that the selected Ollama models are pulled or that pgvector schema migrations are current. Add those checks to the deployment's startup/migration workflow.

## Data protection

The sample Compose database password is for local development only. Never deploy it. Do not log prompts, document contents, API keys or raw tool arguments by default. Define retention periods and user-facing disclosure before collecting conversation memory.
