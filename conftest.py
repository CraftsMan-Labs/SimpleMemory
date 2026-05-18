"""Root conftest with shared async fixtures."""
from __future__ import annotations

import uuid

import pytest


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def workspace_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def source_id() -> uuid.UUID:
    return uuid.uuid4()
