FROM python:3.12-slim AS base

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY api/pyproject.toml api/
COPY shared/pyproject.toml shared/
COPY worker/pyproject.toml worker/
COPY workflows/pyproject.toml workflows/

COPY shared/src/ shared/src/
COPY worker/src/ worker/src/
COPY workflows/ workflows/

RUN uv sync --frozen --no-dev --package kmg-worker 2>/dev/null || uv pip install --system -e ./shared -e ./worker

ENV PYTHONPATH="/app:${PYTHONPATH}"

CMD ["python", "-m", "kmg_worker.main"]
