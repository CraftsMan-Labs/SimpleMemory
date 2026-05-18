"""Test Pydantic schema validation."""
from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from kmg_api.schemas.workspace import CreateWorkspaceRequest
from kmg_api.schemas.source import CreateSourceRequest, PresignedUploadRequest
from kmg_api.schemas.search import SearchRequest
from kmg_api.schemas.canvas import CreateCanvasRequest


class TestWorkspaceSchemas:
    def test_valid_create(self):
        req = CreateWorkspaceRequest(name="Test Project", slug="test-project")
        assert req.name == "Test Project"
        assert req.slug == "test-project"
        assert "wiki_style" in req.settings

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            CreateWorkspaceRequest(name="", slug="test")

    def test_invalid_slug_rejected(self):
        with pytest.raises(ValidationError):
            CreateWorkspaceRequest(name="Test", slug="Invalid Slug!")


class TestSourceSchemas:
    def test_valid_create(self):
        req = CreateSourceRequest(source_type="pdf", title="My Doc")
        assert req.pipeline_id == "default_pdf_pipeline"

    def test_presigned_request(self):
        req = PresignedUploadRequest(source_type="pdf", title="Big File")
        assert req.source_type == "pdf"


class TestSearchSchemas:
    def test_valid_search(self):
        req = SearchRequest(query="What is the architecture?")
        assert req.scope == "current_project"
        assert req.limit == 20

    def test_empty_query_rejected(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="")

    def test_limit_bounds(self):
        with pytest.raises(ValidationError):
            SearchRequest(query="test", limit=0)
        with pytest.raises(ValidationError):
            SearchRequest(query="test", limit=101)


class TestCanvasSchemas:
    def test_valid_create(self):
        req = CreateCanvasRequest(title="My Canvas")
        assert req.layout == {}
