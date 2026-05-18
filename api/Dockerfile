FROM python:3.12-slim AS base

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY api/pyproject.toml api/
COPY shared/pyproject.toml shared/
COPY worker/pyproject.toml worker/
COPY workflows/pyproject.toml workflows/

COPY shared/src/ shared/src/
COPY api/src/ api/src/

RUN uv sync --frozen --no-dev --package kmg-api 2>/dev/null || uv pip install --system -e ./shared -e ./api

EXPOSE 8000

CMD ["uvicorn", "kmg_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
