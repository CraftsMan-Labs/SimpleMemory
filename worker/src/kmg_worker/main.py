"""Worker entrypoint -- starts Redis consumer and workflow runner."""
from __future__ import annotations

import asyncio

import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from kmg_shared.config import settings as shared_settings
from kmg_shared.tracing import configure_tracing
from kmg_shared.adapters.openai_embedding import OpenAIEmbedding
from kmg_shared.adapters.qdrant_db import QdrantVectorDB
from kmg_shared.adapters.redis_cache import RedisCacheAdapter
from kmg_shared.adapters.redis_queue import RedisJobQueue
from kmg_shared.adapters.s3_storage import S3ObjectStorage
from kmg_shared.infra.registry import init_registry
from kmg_shared.repositories.job_repo import JobRepository
from kmg_worker.config import worker_settings
from kmg_worker.consumer import IngestionConsumer
from kmg_worker.job_runner import WorkflowRunner

logger = structlog.get_logger()


async def startup() -> None:
    configure_tracing("kmg-worker", shared_settings.otlp_endpoint or None)
    logger.info("worker_starting", concurrency=worker_settings.worker_concurrency)

    engine = create_async_engine(
        worker_settings.database_url,
        echo=False,
        pool_size=10,
        max_overflow=5,
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    storage = S3ObjectStorage(
        bucket=worker_settings.s3_bucket,
        endpoint_url=worker_settings.s3_endpoint,
        access_key=worker_settings.s3_access_key,
        secret_key=worker_settings.s3_secret_key,
    )
    vector_db = QdrantVectorDB(url=worker_settings.qdrant_url)
    embedding = OpenAIEmbedding(
        api_key=worker_settings.embedding_api_key,
        model=worker_settings.embedding_model,
        dimensions=worker_settings.embedding_dimensions,
    )
    cache = RedisCacheAdapter(url=worker_settings.redis_url)

    init_registry(
        db_session_factory=session_factory,
        storage=storage,
        vector_db=vector_db,
        embedding=embedding,
        cache=cache,
    )

    queue = RedisJobQueue(url=worker_settings.redis_url)
    workflow_runner = WorkflowRunner(simple_agents_client=None)  # TODO: wire SimpleAgents client

    async with session_factory() as session:
        job_repo = JobRepository(session)
        consumer = IngestionConsumer(
            queue=queue,
            job_repo=job_repo,
            workflow_runner=workflow_runner,
        )
        await consumer.run_forever()


def main() -> None:
    asyncio.run(startup())


if __name__ == "__main__":
    main()
