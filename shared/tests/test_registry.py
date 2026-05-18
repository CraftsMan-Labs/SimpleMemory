"""Test the infrastructure registry."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from kmg_shared.infra.registry import (
    get_cache,
    get_db_session,
    get_embedding,
    get_storage,
    get_vector_db,
    init_registry,
    reset_registry,
)


@pytest.fixture(autouse=True)
def _clean_registry():
    """Reset registry before and after each test."""
    reset_registry()
    yield
    reset_registry()


def test_registry_not_initialized_raises():
    with pytest.raises(AssertionError, match="Registry not initialized"):
        get_db_session()

    with pytest.raises(AssertionError, match="Registry not initialized"):
        get_storage()

    with pytest.raises(AssertionError, match="Registry not initialized"):
        get_vector_db()

    with pytest.raises(AssertionError, match="Registry not initialized"):
        get_embedding()

    with pytest.raises(AssertionError, match="Registry not initialized"):
        get_cache()


def test_init_and_get():
    mock_db = MagicMock()
    mock_storage = MagicMock()
    mock_vector = MagicMock()
    mock_embed = MagicMock()
    mock_cache = MagicMock()

    init_registry(
        db_session_factory=mock_db,
        storage=mock_storage,
        vector_db=mock_vector,
        embedding=mock_embed,
        cache=mock_cache,
    )

    assert get_db_session() is mock_db
    assert get_storage() is mock_storage
    assert get_vector_db() is mock_vector
    assert get_embedding() is mock_embed
    assert get_cache() is mock_cache


def test_reset_clears():
    init_registry(
        db_session_factory=MagicMock(),
        storage=MagicMock(),
        vector_db=MagicMock(),
        embedding=MagicMock(),
        cache=MagicMock(),
    )
    reset_registry()

    with pytest.raises(AssertionError):
        get_db_session()
