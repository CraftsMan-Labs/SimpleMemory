"""Test source routes via FastAPI TestClient with overridden deps."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from kmg_api.dependencies import get_request_scope, get_workspace_id, get_source_service
from kmg_api.main import app
from kmg_shared.auth.scoping import RequestScope

TENANT_ID = uuid.uuid4()
WORKSPACE_ID = uuid.uuid4()
SOURCE_ID = uuid.uuid4()
VERSION_ID = uuid.uuid4()
JOB_ID = uuid.uuid4()
NOW = datetime.now(timezone.utc)


def _fake_scope():
    return RequestScope(
        tenant_id=TENANT_ID,
        workspace_id=None,
        user_id=None,
        auth_type="dev_bypass",
        scopes=["read", "write", "admin"],
    )


@pytest.fixture
def mock_source_service():
    return AsyncMock()


@pytest.fixture
def client(mock_source_service):
    app.dependency_overrides[get_request_scope] = lambda: _fake_scope()
    app.dependency_overrides[get_workspace_id] = lambda: WORKSPACE_ID
    app.dependency_overrides[get_source_service] = lambda: mock_source_service
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestCreateSource:
    def test_creates_source_and_job(self, client, mock_source_service):
        fake_source = MagicMock(id=SOURCE_ID)
        fake_version = MagicMock(id=VERSION_ID)
        fake_job = MagicMock(id=JOB_ID)
        mock_source_service.create_source.return_value = (
            fake_source, fake_version, fake_job,
        )

        response = client.post(
            "/v1/sources",
            json={"source_type": "pdf", "title": "My Document"},
            headers={"x-workspace-id": str(WORKSPACE_ID)},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["source_id"] == str(SOURCE_ID)
        assert data["version_id"] == str(VERSION_ID)
        assert data["job_id"] == str(JOB_ID)


class TestPresignedUpload:
    def test_returns_upload_url(self, client, mock_source_service):
        fake_source = MagicMock(id=SOURCE_ID)
        fake_version = MagicMock(id=VERSION_ID)
        mock_source_service.create_presigned_upload.return_value = (
            fake_source, fake_version, "https://s3.example.com/upload?token=abc",
        )

        response = client.post(
            "/v1/sources/presigned",
            json={"source_type": "pdf", "title": "Big File"},
            headers={"x-workspace-id": str(WORKSPACE_ID)},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["source_id"] == str(SOURCE_ID)
        assert "upload_url" in data
        assert data["expires_in"] == 3600


class TestConfirmUpload:
    def test_returns_job(self, client, mock_source_service):
        fake_job = MagicMock(id=JOB_ID)
        mock_source_service.confirm_source_upload.return_value = fake_job

        response = client.post(
            "/v1/sources/confirm",
            json={
                "source_id": str(SOURCE_ID),
                "version_id": str(VERSION_ID),
            },
            headers={"x-workspace-id": str(WORKSPACE_ID)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == str(JOB_ID)
        assert data["status"] == "queued"
