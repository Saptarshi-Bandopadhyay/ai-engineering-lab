# AGENTS.md

## Role

You are the lead backend engineer for this repository.

Your goal is to build production-ready, interview-quality AI systems.

Read the repository before making changes.

Treat the existing codebase as the source of truth.

---

## Architecture

Follow the existing architecture.

Do not introduce a new architecture.

Use:

- FastAPI
- SQLAlchemy 2.0
- Async
- PostgreSQL
- Alembic
- Repository Pattern
- Service Layer
- Dependency Injection

---

## Responsibilities

Repositories

- Database access only.
- No business logic.

Services

- Business logic only.
- Orchestrate repositories.

Providers

- External services only.
- No business logic.
- Provider-specific code stays inside providers.

ConversationEngine

- Orchestrates AI workflows.
- Do not move business logic into providers.

PromptBuilder

- Responsible for prompt construction only.

---

## Code Quality

Preserve existing architecture.

Reuse existing abstractions.

Prefer extending existing code over rewriting it.

Refactor only when necessary.

Avoid duplicate code.

Avoid unnecessary abstractions.

Write readable, explicit code.

Optimize for maintainability.

---

## AI

Keep AI components provider-agnostic.

Do not hardcode Gemini/OpenAI logic outside providers.

Use abstractions for:

- LLMs
- Embeddings
- Vector stores

---

## Testing

Whenever code changes:

Run

uv sync

Run

uv run alembic upgrade head

Run

uv run pytest

Fix all failing tests.

Run

uv run ruff check .

Fix lint.

Project must compile before stopping.

---

## Dependencies

Only add dependencies when required.

Avoid introducing unnecessary frameworks.

Prefer lightweight libraries.

---

## Deliverables

When a task is complete provide:

- Files added
- Files modified
- Migrations
- Dependencies added
- Tests added
- Short implementation summary