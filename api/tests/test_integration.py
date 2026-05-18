"""Integration tests -- require a real Postgres database.

These tests are designed to run against a real database instance, e.g.
via testcontainers-python or a docker-compose test environment.

To run:
    1. Start test services:  docker compose -f docker-compose.yml up -d postgres redis
    2. Set env:              export KMG_DATABASE_URL=postgresql+asyncpg://kmg:kmg_dev_pass@localhost:5432/kmg_test
    3. Run migrations:       alembic -c migrations/alembic.ini upgrade head
    4. Execute:              pytest api/tests/test_integration.py -v

For CI, consider using testcontainers:

    from testcontainers.postgres import PostgresContainer

    @pytest.fixture(scope="session")
    def postgres():
        with PostgresContainer("postgres:16") as pg:
            yield pg

TODO: Implement full integration tests covering:
- Workspace creation -> Source upload -> Ingestion job -> Search
- Concurrent source uploads to same workspace
- Tenant isolation (tenant A cannot read tenant B data)
- Pagination and filtering on list endpoints
"""
from __future__ import annotations

import uuid

import pytest


pytestmark = pytest.mark.skipif(
    True,
    reason="Integration tests require a running Postgres instance. "
           "Set INTEGRATION_TESTS=1 and provide KMG_DATABASE_URL to run.",
)


class TestWorkspaceIntegration:
    @pytest.mark.asyncio
    async def test_full_workspace_lifecycle(self):
        """Create workspace -> update -> list -> verify."""
        pytest.skip("Not yet implemented -- needs testcontainers setup")

    @pytest.mark.asyncio
    async def test_tenant_isolation(self):
        """Ensure tenant A cannot access tenant B's workspaces."""
        pytest.skip("Not yet implemented -- needs testcontainers setup")


class TestSourceIngestionIntegration:
    @pytest.mark.asyncio
    async def test_source_upload_and_job_creation(self):
        """Upload source -> confirm -> verify job is queued."""
        pytest.skip("Not yet implemented -- needs testcontainers setup")

    @pytest.mark.asyncio
    async def test_search_after_ingestion(self):
        """Ingest source -> search -> verify results."""
        pytest.skip("Not yet implemented -- needs testcontainers setup")
