"""Test ingestion workflow handlers with mocked registry."""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class _FakeSessionFactory:
    """Mimics async_sessionmaker: calling it returns an async context manager."""

    def __init__(self, session: AsyncMock):
        self._session = session

    def __call__(self):
        return self._context()

    @asynccontextmanager
    async def _context(self):
        yield self._session


@pytest.fixture(autouse=True)
def _mock_registry():
    """Patch the infra registry so handlers can resolve their dependencies."""
    mock_storage = AsyncMock()
    mock_embedding = AsyncMock()
    mock_vector_db = AsyncMock()
    mock_session = AsyncMock()
    mock_session_factory = _FakeSessionFactory(mock_session)

    with (
        patch("workflows.ingestion.handlers.get_storage", return_value=mock_storage),
        patch("workflows.ingestion.handlers.get_embedding", return_value=mock_embedding),
        patch("workflows.ingestion.handlers.get_vector_db", return_value=mock_vector_db),
        patch("workflows.ingestion.handlers.get_db_session", return_value=mock_session_factory),
    ):
        yield {
            "storage": mock_storage,
            "embedding": mock_embedding,
            "vector_db": mock_vector_db,
            "session_factory": mock_session_factory,
            "session": mock_session,
        }


class TestParseSource:
    def test_reads_from_storage(self, _mock_registry):
        from workflows.ingestion.handlers import parse_source

        mock_storage = _mock_registry["storage"]
        mock_storage.get.return_value = b"Hello world, this is a test document."

        payload = {
            "tenant_id": str(uuid.uuid4()),
            "workspace_id": str(uuid.uuid4()),
            "source_id": str(uuid.uuid4()),
            "source_version_id": str(uuid.uuid4()),
            "source_type": "txt",
        }

        result = parse_source({}, payload)

        mock_storage.get.assert_awaited_once()
        assert result["raw_text"] == "Hello world, this is a test document."
        assert result["metadata"]["source_type"] == "txt"
        assert result["metadata"]["char_count"] == len("Hello world, this is a test document.")

    def test_handles_pdf_type(self, _mock_registry):
        from workflows.ingestion.handlers import parse_source

        mock_storage = _mock_registry["storage"]
        mock_storage.get.return_value = b"Page 1 content\fPage 2 content"

        payload = {
            "tenant_id": str(uuid.uuid4()),
            "workspace_id": str(uuid.uuid4()),
            "source_id": str(uuid.uuid4()),
            "source_version_id": str(uuid.uuid4()),
            "source_type": "pdf",
        }

        result = parse_source({}, payload)
        assert result["page_count"] == 2


class TestEmbedChunks:
    def test_calls_embedding_and_vector_db(self, _mock_registry):
        from workflows.ingestion.handlers import embed_chunks

        mock_embedding = _mock_registry["embedding"]
        mock_vector_db = _mock_registry["vector_db"]
        mock_session = _mock_registry["session"]

        chunk_id = uuid.uuid4()
        fake_chunk = MagicMock()
        fake_chunk.id = chunk_id
        fake_chunk.content = "Test chunk content"
        fake_chunk.source_id = uuid.uuid4()
        fake_chunk.chunk_index = 0

        mock_repo = AsyncMock()
        mock_repo.get_by_ids.return_value = [fake_chunk]

        with patch("workflows.ingestion.handlers.ChunkRepository", return_value=mock_repo):
            mock_embedding.embed_texts.return_value = [[0.1] * 1536]
            mock_embedding.model_name = "text-embedding-3-small"
            mock_vector_db.upsert.return_value = 1

            payload = {
                "tenant_id": str(uuid.uuid4()),
                "workspace_id": str(uuid.uuid4()),
                "chunk_ids": [str(chunk_id)],
            }

            result = embed_chunks({}, payload)

            mock_embedding.embed_texts.assert_awaited()
            mock_vector_db.upsert.assert_awaited_once()
            assert result["vectors_upserted"] == 1
