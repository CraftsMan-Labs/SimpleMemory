from kmg_shared.config import Settings


class WorkerSettings(Settings):
    model_config = {"env_prefix": "KMG_"}

    worker_concurrency: int = 4
    job_timeout_seconds: int = 600
    retry_max_attempts: int = 3


worker_settings = WorkerSettings()
