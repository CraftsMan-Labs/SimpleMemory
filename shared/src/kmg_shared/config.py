import sys

from pydantic import ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "KMG_"}

    database_url: str = "postgresql+asyncpg://kmg:kmg_dev_pass@localhost:5432/kmg_dev"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "kmg-sources"

    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    otlp_endpoint: str = ""

    log_level: str = "INFO"
    log_format: str = "json"


try:
    settings = Settings()
except ValidationError as exc:
    print("FATAL: Configuration validation failed. Missing or invalid environment variables:\n")
    for error in exc.errors():
        loc = " -> ".join(str(l) for l in error["loc"])
        print(f"  KMG_{loc.upper()}: {error['msg']}")
    print("\nSet the required KMG_* environment variables and restart.")
    sys.exit(1)
