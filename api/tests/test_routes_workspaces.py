"""Test workspace CRUD via FastAPI TestClient with overridden deps."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from kmg_api.dependencies import get_db_session, get_request_scope, get_workspace_service
from kmg_api.main import app
from kmg_shared.auth.scoping import RequestScope
from kmg_shared.errors import NotFoundError

TENANT_ID = uuid.uuid4()
WORKSPACE_ID = uuid.uuid4()
NOW = datetime.now(timezone.utc)


def _fake_scope():
    return RequestScope(
        tenant_id=TENANT_ID,
        workspace_id=None,
        user_id=None,
        auth_type="dev_bypass",
        scopes=["read", "write", "admin"],
    )


def _make_workspace(ws_id=None, name="Test Project", slug="test-project"):
    ws = MagicMock()
    ws.id = ws_id or WORKSPACE_ID
    ws.tenant_id = TENANT_ID
    ws.name = name
    ws.slug = slug
    ws.status = "active"
    ws.settings = {"wiki_style": "obsidian_like"}
    ws.created_at = NOW
    ws.updated_at = NOW
    return ws


@pytest.fixture
def mock_ws_service():
    return AsyncMock()


@pytest.fixture
def client(mock_ws_service):
    app.dependency_overrides[get_request_scope] = lambda: _fake_scope()
    app.dependency_overrides[get_workspace_service] = lambda: mock_ws_service
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestCreateWorkspace:
    def test_creates_workspace(self, client, mock_ws_service):
        mock_ws_service.create_workspace.return_value = _make_workspace()

        response = client.post("/v1/workspaces", json={
            "name": "Test Project",
            "slug": "test-project",
        })

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["slug"] == "test-project"
        mock_ws_service.create_workspace.assert_awaited_once()


class TestListWorkspaces:
    def test_lists_workspaces(self, client, mock_ws_service):
        ws1 = _make_workspace(ws_id=uuid.uuid4(), name="WS 1", slug="ws-1")
        ws2 = _make_workspace(ws_id=uuid.uuid4(), name="WS 2", slug="ws-2")
        mock_ws_service.list_workspaces.return_value = [ws1, ws2]

        response = client.get("/v1/workspaces")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["workspaces"]) == 2


class TestGetWorkspace:
    def test_returns_workspace(self, client, mock_ws_service):
        mock_ws_service.get_workspace.return_value = _make_workspace()

        response = client.get(f"/v1/workspaces/{WORKSPACE_ID}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(WORKSPACE_ID)

    def test_returns_404_when_not_found(self, client, mock_ws_service):
        mock_ws_service.get_workspace.side_effect = NotFoundError("Workspace", WORKSPACE_ID)

        response = client.get(f"/v1/workspaces/{WORKSPACE_ID}")

        assert response.status_code == 404
        assert "Workspace" in response.json()["entity"]
