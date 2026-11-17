# Enterprise AI Assistant

A production-oriented, locally runnable enterprise AI assistant built incrementally with FastAPI, Ollama, LangChain, PostgreSQL/pgvector, MCP, and an evaluation-first engineering workflow.

> **Project status:** Phase 1 — requirements and architecture baseline. Application code will be added in later phases.

## What we are building

The assistant will let an authenticated user:
- Ask questions over an explicitly ingested document collection.
- Receive answers grounded in retrieved passages with source references.
- Search the web through a controlled search provider adapter.
- Invoke approved tools through validated tool contracts and MCP.
- Run bounded, observable multi-step investigations.
- Inspect request traces, retrieval results, tool calls, latency, and token usage.
- Evaluate prompt, retrieval, answer, and agent quality before releases.

The system must distinguish retrieved evidence from model-generated reasoning. It must not invent facts, citations, tool results, or successful actions.

## Architecture principles

1. **Local-first development:** Ollama is the default inference runtime.
2. **Evidence before confidence:** answers based on documents must cite retrieved sources.
3. **Explicit orchestration:** the application owns state, authorization, retries, and limits.
4. **Least privilege:** tools are allow-listed and independently authorized.
5. **Evaluation before release:** changes are tested against versioned datasets and release thresholds.
6. **Observable by design:** request, retrieval, model, and tool boundaries emit structured telemetry.
7. **Replaceable components:** provider-specific code stays behind interfaces.
8. **No hidden infrastructure:** local development is reproducible with documented commands.

## Planned technology stack

| Concern | Initial choice |
|---|---|
| API | FastAPI |
| Runtime | Python 3.12 |
| LLM inference | Ollama |
| Initial chat model | llama3.2:3b (configurable) |
| Orchestration | LangChain; LangGraph where explicit stateful workflows are needed |
| Database | PostgreSQL |
| Vector search | pgvector |
| Tool protocol | MCP |
| Observability | Langfuse plus structured application logs |
| Configuration | Environment variables with validated settings |
| Tests | pytest |
| Local infrastructure | Docker Compose |

Exact package versions will be pinned and validated when implementation begins. Do not assume a tutorial written against one LangChain or MCP release works unchanged against another.

## Repository map

~~~
.
├── README.md
├── .env.example
├── .gitignore
└── docs/
    ├── 01-requirements-and-scope.md
    ├── 02-system-architecture.md
    ├── 03-technology-decisions.md
    └── 04-implementation-roadmap.md
~~~

The structure will grow as implementation phases introduce application code, tests, migrations, examples, and deployment configuration.

## Development approach

Every implementation phase should include:
- A concept explanation and the reason for the design.
- A clear file-by-file implementation.
- Runnable commands and expected behavior.
- Unit and integration tests appropriate to the component.
- Failure modes, security concerns, and operational notes.
- A Git commit with a focused message.

A committed test is not the same as an executed test. Test results will be reported only after execution in an available environment.

## Getting started

At this phase, the repository contains design documentation only.

~~~bash
git clone https://github.com/BharatJogi777/Enterprise-AI-Assistant.git
cd Enterprise-AI-Assistant
git checkout master
~~~

Read the documents in this order:
1. [Requirements and scope](docs/01-requirements-and-scope.md)
2. [System architecture](docs/02-system-architecture.md)
3. [Technology decisions](docs/03-technology-decisions.md)
4. [Implementation roadmap](docs/04-implementation-roadmap.md)

## Non-goals for the first release

- Training a foundation model from scratch.
- Unrestricted autonomous agents.
- Executing arbitrary shell commands from natural-language requests.
- Automatically trusting content retrieved from the web or uploaded documents.
- Multi-tenant enterprise billing and complex organization administration.
- Production deployment to a public environment before authentication, authorization, secrets, and operational controls are implemented.

## License

No license has been selected yet. Until one is added, do not assume this repository grants permission to reuse or redistribute its contents.
