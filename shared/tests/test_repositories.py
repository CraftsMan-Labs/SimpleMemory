"""Test base repository and key repository methods."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from kmg_shared.errors import NotFoundError
from kmg_shared.repositories.base_repo import BaseRepository
from kmg_shared.db.models.base import Base


class FakeModel(Base):
    __tablename__ = "fake_models"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("tenants.id"))
    workspace_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("workspaces.id"))


class FakeRepository(BaseRepository[FakeModel]):
    model = FakeModel


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repo(mock_session):
    return FakeRepository(mock_session)


class TestGetById:
    @pytest.mark.asyncio
    async def test_returns_model_when_found(self, repo, mock_session):
        expected = FakeModel(id=uuid.uuid4())
        mock_session.get.return_value = expected
        result = await repo.get_by_id(expected.id)
        assert result is expected
        mock_session.get.assert_awaited_once_with(FakeModel, expected.id)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, repo, mock_session):
        mock_session.get.return_value = None
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None


class TestGetByIdOrRaise:
    @pytest.mark.asyncio
    async def test_returns_model_when_found(self, repo, mock_session):
        expected = FakeModel(id=uuid.uuid4())
        mock_session.get.return_value = expected
        result = await repo.get_by_id_or_raise(expected.id)
        assert result is expected

    @pytest.mark.asyncio
    async def test_raises_not_found_error(self, repo, mock_session):
        mock_session.get.return_value = None
        with pytest.raises(NotFoundError) as exc_info:
            await repo.get_by_id_or_raise(uuid.uuid4())
        assert exc_info.value.entity == "FakeModel"


class TestListByWorkspace:
    @pytest.mark.asyncio
    async def test_filters_by_tenant_and_workspace(self, repo, mock_session):
        tid = uuid.uuid4()
        wid = uuid.uuid4()

        fake_items = [FakeModel(id=uuid.uuid4()), FakeModel(id=uuid.uuid4())]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = fake_items
        mock_session.execute.return_value = mock_result

        result = await repo.list_by_workspace(tid, wid, limit=10, offset=0)

        assert result == fake_items
        mock_session.execute.assert_awaited_once()
        stmt = mock_session.execute.call_args[0][0]
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": False}))
        assert "fake_models" in compiled.lower()

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await repo.list_by_workspace(uuid.uuid4(), uuid.uuid4())
        assert result == []
