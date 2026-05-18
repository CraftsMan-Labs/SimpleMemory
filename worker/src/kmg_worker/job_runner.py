from __future__ import annotations

from pathlib import Path

import structlog

from kmg_shared.db.models.job import IngestionJob

logger = structlog.get_logger()

WORKFLOW_DIR = Path(__file__).resolve().parents[3] / "workflows"


class WorkflowRunner:
    """Runs SimpleAgents YAML workflows for ingestion jobs.

    The SimpleAgents client is initialized at worker startup.
    Workflows are chained: ingestion -> wiki -> graph.
    """

    def __init__(self, simple_agents_client: object) -> None:
        self._client = simple_agents_client

    async def run_ingestion(self, job: IngestionJob) -> None:
        """Run the full ingestion pipeline: parse/chunk -> wiki -> graph."""
        workflow_input = {
            "tenant_id": str(job.tenant_id),
            "workspace_id": str(job.workspace_id),
            "source_id": str(job.source_id),
            "source_version_id": str(job.source_version_id),
            "pipeline_id": job.pipeline_id,
        }

        # Stage 1: Ingestion (parse, segment, chunk, embed)
        logger.info("workflow_stage_start", stage="ingestion", job_id=str(job.id))
        ingestion_result = self._run_workflow(
            "ingestion/source_ingest.yaml", workflow_input
        )
        chunk_ids = ingestion_result.get("outputs", {}).get("create_chunks", {}).get("output", {}).get("chunk_ids", [])

        # Stage 2: Wiki generation
        logger.info("workflow_stage_start", stage="wiki", job_id=str(job.id))
        wiki_input = {**workflow_input, "chunk_ids": chunk_ids}
        wiki_result = self._run_workflow("wiki/wiki_generate.yaml", wiki_input)
        wiki_page_ids = wiki_result.get("outputs", {}).get("persist_wiki", {}).get("output", {}).get("wiki_page_ids", [])

        # Stage 3: Graph building
        logger.info("workflow_stage_start", stage="graph", job_id=str(job.id))
        graph_input = {**workflow_input, "chunk_ids": chunk_ids, "wiki_page_ids": wiki_page_ids}
        self._run_workflow("graph/graph_build.yaml", graph_input)

        logger.info("workflow_complete", job_id=str(job.id))

    def _run_workflow(self, workflow_path: str, input_data: dict) -> dict:
        """Execute a single SimpleAgents workflow.

        Uses the SimpleAgents Python client. For now, this is a placeholder
        that will be wired to the actual client at startup.
        """
        full_path = str(WORKFLOW_DIR / workflow_path)

        # Placeholder -- actual implementation depends on SimpleAgents client API:
        # from simple_agents_py import Client
        # from simple_agents_py.workflow_request import WorkflowExecutionRequest, WorkflowMessage, WorkflowRole
        # req = WorkflowExecutionRequest(
        #     workflow_path=full_path,
        #     input=input_data,
        #     messages=[WorkflowMessage(role=WorkflowRole.USER, content="Process this source.")],
        # )
        # result = self._client.run_workflow(req)
        # return result.to_dict()

        logger.info("workflow_executed", path=workflow_path, input_keys=list(input_data.keys()))
        return {"status": "completed", "outputs": {}}
