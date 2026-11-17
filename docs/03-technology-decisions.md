# 03 — Technology Decisions

This document records the initial choices and why they were selected. Decisions can change when implementation evidence or operational requirements justify a change.

## Decision 1 — Python 3.12

**Choice:** Python 3.12.

**Why:** Strong ecosystem support for FastAPI, LangChain, MCP clients, evaluation tooling, and data/ML libraries. A modern supported runtime avoids dependency constraints of older system Python installations.

**Trade-off:** Some native packages may require compatible wheels or build tooling. Pin versions and verify installation on the target machine.

## Decision 2 — FastAPI for the API

**Choice:** FastAPI with Pydantic request/response models.

**Why:** Typed HTTP contracts, dependency injection, automatic OpenAPI documentation, async support, and a familiar separation between routers and application services.

**Trade-off:** Async syntax does not automatically make blocking database or model calls non-blocking. Use appropriate clients and isolate blocking work.

## Decision 3 — Ollama as the initial inference runtime

**Choice:** Ollama on the local machine.

**Why:** Local experimentation, no per-token API bill, straightforward model switching, and a practical way to understand inference integration.

**Initial model candidates:** llama3.2:3b for lightweight instruction following; qwen3:4b as an alternative for comparative evaluation.

**Trade-off:** A small local model has limited reasoning quality and memory. Model quality, context size, throughput, and concurrency must be measured on the actual machine. Do not use a small model as a substitute for authorization or deterministic validation.

## Decision 4 — LangChain, with LangGraph for explicit stateful workflows

**Choice:** Use LangChain for model/provider abstractions, prompt composition, and selected integrations. Introduce LangGraph when workflows require explicit state, branching, checkpoints, or resumability.

**Why:** The project is intended to teach and apply the ecosystem while keeping application logic visible.

**Trade-off:** Framework APIs evolve. Pin compatible package versions, isolate framework-specific code, and do not allow framework abstractions to obscure authorization, transactions, or error handling.

**Important:** The first implementation should begin with a simple deterministic request path. Add agent loops only when a use case needs them.

## Decision 5 — PostgreSQL + pgvector

**Choice:** PostgreSQL as the primary relational database with pgvector for vector similarity search.

**Why:** One database can store users, documents, chunks, metadata, and vectors; transactions and SQL filters are useful for correctness and authorization-aware retrieval.

**Trade-off:** At larger scale or specialized search needs, dedicated vector or search infrastructure may be justified. Benchmark before migrating.

**Embedding compatibility:** The embedding model and vector dimension must be stored/configured consistently. A model or dimension change requires an explicit migration/re-embedding plan.

## Decision 6 — MCP for external tools

**Choice:** Integrate MCP through a controlled client and configured server registry.

**Why:** Standardized tool discovery and invocation across separate tool servers.

**Trade-off:** MCP does not solve identity, authorization, approval, idempotency, or business policy. Those remain responsibilities of this application. Treat tool descriptions and results as untrusted.

## Decision 7 — Langfuse for LLM observability

**Choice:** Langfuse for traces and model/application observations, alongside normal structured logs and metrics.

**Why:** LLM applications need visibility into prompts, generations, retrieval, tool calls, and evaluation outcomes.

**Trade-off:** Telemetry can contain sensitive content and creates an external dependency if hosted. Minimize captured content, configure retention/access, and make telemetry failure non-fatal unless a deployment policy explicitly requires it.

## Decision 8 — pytest and deterministic fakes

**Choice:** pytest for unit and integration tests; fake model, embedding, search, and tool adapters for deterministic tests.

**Why:** Most correctness and policy behavior should be testable without a running model or network.

**Trade-off:** Fake tests do not establish real model quality. Maintain a separate, explicit model smoke-test and evaluation suite.

## Decision 9 — Docker Compose for local infrastructure

**Choice:** Docker Compose for PostgreSQL/pgvector and supporting local services.

**Why:** Reproducible dependencies and simple lifecycle management.

**Trade-off:** Containers consume memory. Keep Ollama on the host and avoid starting optional observability services unless needed.

## Decision 10 — Modular monolith before microservices

**Choice:** One deployable API with layered modules and provider adapters.

**Why:** The first goal is to build a correct end-to-end system with low operational overhead.

**Trade-off:** A single process has a shared failure and scaling boundary. Ingestion workers or model-serving components can be separated later based on measured load and isolation requirements.

## Initial dependency policy

- Use a supported Python runtime.
- Pin direct dependencies and commit a lock file when implementation starts.
- Upgrade one integration boundary at a time.
- Run tests after upgrades.
- Avoid unbounded dependency ranges in a production deployment.
- Record the tested versions in project documentation.

## Decision review triggers

Revisit decisions when:
- Local model latency or quality fails the use case.
- Vector retrieval misses relevant documents at the required scale.
- API and ingestion workloads interfere with each other.
- MCP tool isolation or permission requirements exceed the current design.
- Observability cost, privacy, or availability becomes unacceptable.
- Measured traffic requires independent scaling.
