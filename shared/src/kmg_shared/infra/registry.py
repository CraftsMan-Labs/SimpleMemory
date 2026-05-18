from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from kmg_shared.ports.cache import Cache
    from kmg_shared.ports.embedding import EmbeddingProvider
    from kmg_shared.ports.queue import JobQueue
    from kmg_shared.ports.storage import ObjectStorage
    from kmg_shared.ports.vector_db import VectorDB

_db_session_factory: async_sessionmaker[AsyncSession] | None = None
_storage: ObjectStorage | None = None
_vector_db: VectorDB | None = None
_embedding: EmbeddingProvider | None = None
_cache: Cache | None = None
_queue: JobQueue | None = None


def init_registry(
    *,
    db_session_factory: async_sessionmaker[AsyncSession],
    storage: ObjectStorage,
    vector_db: VectorDB,
    embedding: EmbeddingProvider,
    cache: Cache,
    queue: JobQueue | None = None,
) -> None:
    """Called once at worker startup after constructing all adapters."""
    global _db_session_factory, _storage, _vector_db, _embedding, _cache, _queue
    _db_session_factory = db_session_factory
    _storage = storage
    _vector_db = vector_db
    _embedding = embedding
    _cache = cache
    _queue = queue


def get_db_session() -> async_sessionmaker[AsyncSession]:
    assert _db_session_factory is not None, "Registry not initialized -- call init_registry() first"
    return _db_session_factory


def get_storage() -> ObjectStorage:
    assert _storage is not None, "Registry not initialized -- call init_registry() first"
    return _storage


def get_vector_db() -> VectorDB:
    assert _vector_db is not None, "Registry not initialized -- call init_registry() first"
    return _vector_db


def get_embedding() -> EmbeddingProvider:
    assert _embedding is not None, "Registry not initialized -- call init_registry() first"
    return _embedding


def get_cache() -> Cache:
    assert _cache is not None, "Registry not initialized -- call init_registry() first"
    return _cache


def get_queue() -> JobQueue:
    assert _queue is not None, "Registry not initialized -- call init_registry() first"
    return _queue


def reset_registry() -> None:
    """For testing -- reset all registry entries."""
    global _db_session_factory, _storage, _vector_db, _embedding, _cache, _queue
    _db_session_factory = None
    _storage = None
    _vector_db = None
    _embedding = None
    _cache = None
    _queue = None
