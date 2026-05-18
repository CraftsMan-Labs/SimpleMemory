"""Test wiki workflow handlers with mocked registry."""
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
    mock_embedding = AsyncMock()
    mock_vector_db = AsyncMock()
    mock_session = AsyncMock()
    mock_session_factory = _FakeSessionFactory(mock_session)

    with (
        patch("workflows.wiki.handlers.get_embedding", return_value=mock_embedding),
        patch("workflows.wiki.handlers.get_vector_db", return_value=mock_vector_db),
        patch("workflows.wiki.handlers.get_db_session", return_value=mock_session_factory),
    ):
        yield {
            "embedding": mock_embedding,
            "vector_db": mock_vector_db,
            "session_factory": mock_session_factory,
            "session": mock_session,
        }


class TestPersistWiki:
    def test_creates_pages_links_and_evidence(self, _mock_registry):
        from workflows.wiki.handlers import persist_wiki

        mock_session = _mock_registry["session"]
        mock_repo = AsyncMock()
        mock_repo.get_page_by_slug.return_value = None

        page_id_1 = uuid.uuid4()
        page_id_2 = uuid.uuid4()
        fake_page_1 = MagicMock(id=page_id_1)
        fake_page_2 = MagicMock(id=page_id_2)
        mock_repo.create_page.side_effect = [fake_page_1, fake_page_2]

        with patch("workflows.wiki.handlers.WikiRepository", return_value=mock_repo):
            payload = {
                "tenant_id": str(uuid.uuid4()),
                "workspace_id": str(uuid.uuid4()),
                "source_id": str(uuid.uuid4()),
                "source_version_id": str(uuid.uuid4()),
                "wiki_pages": [
                    {
                        "slug": "page-one",
                        "title": "Page One",
                        "page_type": "concept",
                        "markdown": "# Page One\nContent here",
                        "evidence_chunk_ids": [str(uuid.uuid4())],
                    },
                    {
                        "slug": "page-two",
                        "title": "Page Two",
                        "page_type": "concept",
                        "markdown": "# Page Two\nMore content",
                    },
                ],
                "wiki_links": [
                    {
                        "from_slug": "page-one",
                        "to_slug": "page-two",
                        "link_text": "Page Two",
                        "link_type": "reference",
                    }
                ],
            }

            result = persist_wiki({}, payload)

            assert len(result["wiki_page_ids"]) == 2
            assert len(result["wiki_link_ids"]) == 1
            assert mock_repo.create_page.await_count == 2
            mock_repo.create_revision.assert_awaited()
            mock_repo.create_evidence_batch.assert_awaited()
            mock_repo.create_links_batch.assert_awaited_once()
            mock_repo.create_backlinks_batch.assert_awaited_once()


class TestEmbedWiki:
    def test_calls_embedding_api(self, _mock_registry):
        from workflows.wiki.handlers import embed_wiki

        mock_embedding = _mock_registry["embedding"]
        mock_vector_db = _mock_registry["vector_db"]
        mock_session = _mock_registry["session"]

        page_id = uuid.uuid4()
        fake_page = MagicMock()
        fake_page.id = page_id
        fake_page.title = "Test Page"
        fake_page.slug = "test-page"
        fake_page.summary = "A test page"
        fake_page.markdown = "# Test\nContent"
        fake_page.page_type = "concept"

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [fake_page]
        mock_session.execute.return_value = mock_result

        mock_embedding.embed_texts.return_value = [[0.1] * 1536]
        mock_embedding.model_name = "text-embedding-3-small"
        mock_vector_db.upsert.return_value = 1

        payload = {
            "tenant_id": str(uuid.uuid4()),
            "workspace_id": str(uuid.uuid4()),
            "wiki_page_ids": [str(page_id)],
        }

        result = embed_wiki({}, payload)

        mock_embedding.embed_texts.assert_awaited_once()
        mock_vector_db.upsert.assert_awaited_once()
        assert result["vectors_upserted"] == 1

    def test_returns_zero_for_empty_ids(self, _mock_registry):
        from workflows.wiki.handlers import embed_wiki

        payload = {
            "tenant_id": str(uuid.uuid4()),
            "workspace_id": str(uuid.uuid4()),
            "wiki_page_ids": [],
        }

        result = embed_wiki({}, payload)
        assert result["vectors_upserted"] == 0
