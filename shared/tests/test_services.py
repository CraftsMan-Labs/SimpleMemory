"""Test service classes with mocked repos and ports."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from kmg_shared.errors import NotFoundError, SourceUploadNotFoundError
from kmg_shared.services.source_service import SourceService
from kmg_shared.services.search_service import SearchService, SearchResult
from kmg_shared.services.workspace_service import WorkspaceService
from kmg_shared.ports.vector_db import ScoredResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tenant_id():
    return uuid.uuid4()


@pytest.fixture
def workspace_id():
    return uuid.uuid4()


@pytest.fixture
def source_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def job_repo():
    return AsyncMock()


@pytest.fixture
def storage():
    return AsyncMock()


@pytest.fixture
def queue():
    return AsyncMock()


@pytest.fixture
def source_service(source_repo, job_repo, storage, queue):
    return SourceService(
        source_repo=source_repo,
        job_repo=job_repo,
        storage=storage,
        queue=queue,
    )


# ---------------------------------------------------------------------------
# SourceService tests
# ---------------------------------------------------------------------------

class TestSourceServiceCreateSource:
    @pytest.mark.asyncio
    async def test_creates_source_version_and_job(
        self, source_service, source_repo, job_repo, storage, queue, tenant_id, workspace_id
    ):
        fake_source = MagicMock(id=uuid.uuid4())
        fake_version = MagicMock(id=uuid.uuid4())
        fake_job = MagicMock(id=uuid.uuid4())

        source_repo.create.return_value = fake_source
        source_repo.create_version.return_value = fake_version
        job_repo.create.return_value = fake_job

        source, version, job = await source_service.create_source(
            tenant_id, workspace_id,
            source_type="pdf", title="Test Doc",
        )

        assert source is fake_source
        assert version is fake_version
        assert job is fake_job
        source_repo.create.assert_awaited_once()
        source_repo.create_version.assert_awaited_once()
        job_repo.create.assert_awaited_once()
        queue.enqueue.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uploads_raw_content_when_provided(
        self, source_service, source_repo, job_repo, storage, queue, tenant_id, workspace_id
    ):
        source_repo.create.return_value = MagicMock(id=uuid.uuid4())
        source_repo.create_version.return_value = MagicMock(id=uuid.uuid4())
        job_repo.create.return_value = MagicMock(id=uuid.uuid4())

        await source_service.create_source(
            tenant_id, workspace_id,
            source_type="txt", title="Test",
            raw_content=b"hello world",
        )

        storage.put.assert_awaited_once()
        args = storage.put.call_args
        assert args[0][1] == b"hello world"


class TestSourceServiceConfirmUpload:
    @pytest.mark.asyncio
    async def test_raises_when_object_not_found(
        self, source_service, source_repo, storage, tenant_id, workspace_id
    ):
        sid = uuid.uuid4()
        vid = uuid.uuid4()
        fake_source = MagicMock(id=sid, tenant_id=tenant_id)
        source_repo.get_by_id.return_value = fake_source
        storage.exists.return_value = False

        with pytest.raises(SourceUploadNotFoundError):
            await source_service.confirm_source_upload(
                tenant_id, workspace_id, sid, vid,
            )

    @pytest.mark.asyncio
    async def test_raises_when_source_not_found(
        self, source_service, source_repo, tenant_id, workspace_id
    ):
        source_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await source_service.confirm_source_upload(
                tenant_id, workspace_id, uuid.uuid4(), uuid.uuid4(),
            )


# ---------------------------------------------------------------------------
# SearchService tests
# ---------------------------------------------------------------------------

class TestSearchServiceSearch:
    @pytest.mark.asyncio
    async def test_calls_embed_text_and_vector_db_search(self, tenant_id, workspace_id):
        embedding = AsyncMock()
        embedding.embed_text.return_value = [0.1] * 1536

        vector_db = AsyncMock()
        result_id = str(uuid.uuid4())
        vector_db.search.return_value = [
            ScoredResult(
                id=result_id,
                score=0.95,
                payload={
                    "record_type": "wiki_page",
                    "title": "Test Page",
                    "slug": "test-page",
                    "snippet": "Some text",
                    "workspace_id": str(workspace_id),
                },
            )
        ]

        session_factory = AsyncMock()
        service = SearchService(
            embedding=embedding,
            vector_db=vector_db,
            session_factory=session_factory,
        )

        result = await service.search(
            tenant_id, workspace_id, "test query",
        )

        embedding.embed_text.assert_awaited_once_with("test query")
        vector_db.search.assert_awaited_once()
        assert isinstance(result, SearchResult)
        assert len(result.results) == 1
        assert result.results[0].title == "Test Page"
        assert result.results[0].score == 0.95


# ---------------------------------------------------------------------------
# WorkspaceService tests
# ---------------------------------------------------------------------------

class TestWorkspaceServiceCRUD:
    @pytest.mark.asyncio
    async def test_create_workspace(self, tenant_id):
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        service = WorkspaceService(session)

        result = await service.create_workspace(
            tenant_id, name="Test", slug="test",
        )

        session.add.assert_called_once()
        session.flush.assert_awaited_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_workspace_raises_not_found(self, tenant_id, workspace_id):
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        service = WorkspaceService(session)

        with pytest.raises(NotFoundError):
            await service.get_workspace(tenant_id, workspace_id)

    @pytest.mark.asyncio
    async def test_list_workspaces(self, tenant_id):
        session = AsyncMock()
        fake_ws = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = fake_ws
        session.execute.return_value = mock_result

        service = WorkspaceService(session)
        result = await service.list_workspaces(tenant_id)

        assert result == fake_ws
        session.execute.assert_awaited_once()
