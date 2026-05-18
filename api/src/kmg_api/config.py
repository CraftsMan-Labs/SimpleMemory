from kmg_shared.config import Settings


class ApiSettings(Settings):
    model_config = {"env_prefix": "KMG_"}

    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    cors_origins: list[str] = ["http://localhost:3000"]


api_settings = ApiSettings()
