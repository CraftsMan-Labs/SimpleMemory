# Knowledge Memory Graph (KMG) v3

A multi-tenant knowledge management platform that ingests documents, builds knowledge graphs, and provides intelligent search via a project-base/wiki architecture.

## Architecture

KMG v3 is a Python monorepo managed with [uv workspaces](https://docs.astral.sh/uv/concepts/workspaces/), consisting of four packages:

| Package | Description |
|---|---|
| `api` | FastAPI HTTP service — REST endpoints, auth middleware, request validation |
| `worker` | Background job consumer — processes async tasks from Redis queues |
| `shared` | Shared library — DB models, repositories, services, config, adapters |
| `workflows` | Workflow definitions — ingestion, wiki, graph, search, and canvas pipelines |

## Quick Start

### 1. Start infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL 16, Redis 7, Qdrant, and MinIO (S3-compatible storage).

### 2. Install dependencies

```bash
uv sync
```

### 3. Run database migrations

```bash
cd migrations
alembic upgrade head
```

### 4. Start the API server

```bash
uv run uvicorn kmg_api.main:app --reload
```

### 5. Start the worker

```bash
uv run python -m kmg_worker.main
```

## Project Structure

```
├── api/                    # FastAPI service
│   ├── src/kmg_api/
│   │   ├── middleware/     # Auth, logging, error handling
│   │   ├── routes/         # API route handlers
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── config.py       # API-specific settings
│   │   ├── dependencies.py # FastAPI DI providers
│   │   └── main.py         # App factory
│   └── tests/
├── worker/                 # Background job consumer
│   ├── src/kmg_worker/
│   │   ├── config.py       # Worker-specific settings
│   │   └── main.py         # Worker entrypoint
│   └── tests/
├── shared/                 # Shared library
│   ├── src/kmg_shared/
│   │   ├── adapters/       # Infrastructure adapters (S3, Qdrant, Redis)
│   │   ├── auth/           # JWT, password hashing, RBAC
│   │   ├── db/models/      # SQLAlchemy ORM models
│   │   ├── infra/          # DB engine, session factory
│   │   ├── ports/          # Abstract interfaces (ports)
│   │   ├── repositories/   # Data access layer
│   │   ├── services/       # Business logic / domain services
│   │   └── config.py       # Base settings (env vars)
│   └── tests/
├── workflows/              # Workflow pipelines
│   ├── ingestion/          # Document ingestion pipeline
│   ├── wiki/               # Wiki page generation
│   ├── graph/              # Knowledge graph construction
│   ├── search/             # Hybrid search pipeline
│   ├── canvas/             # Canvas layout pipeline
│   └── tests/
├── migrations/             # Alembic database migrations
│   ├── versions/
│   ├── alembic.ini
│   ├── env.py
│   └── script.py.mako
├── docker-compose.yml      # Local infrastructure
└── pyproject.toml          # Root workspace config
```

## Configuration

All settings are configured via environment variables with the `KMG_` prefix. See `shared/src/kmg_shared/config.py` for defaults.

## Development

```bash
# Lint
uv run ruff check .

# Type check
uv run mypy .

# Test
uv run pytest
```
