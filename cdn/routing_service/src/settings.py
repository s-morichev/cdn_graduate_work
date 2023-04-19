from logging import getLogger

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    storage_access_key: str = Field("admin", env="MINIO_USER")
    storage_secret_key: str = Field("supersecret", env="MINIO_PASSWORD")

    bucket: str = Field("test", env="MOVIES_BUCKET")

    # JWT
    jwn_secret_key: str = Field("secret_jwt_key", env="UGC_JWT_KEY")
    mock_auth_token: bool = Field(
        False, env="UGC_MOCK_AUTH_TOKEN"
    )  # для отладки - можно отключить проверку токена в заголовках

    sync_service_url = Field("http://localhost:8010", env="SYNC_SERVICE_URL")
    ugc_service_url = Field("http://localhost:8010", env="SYNC_SERVICE_URL")

    class Config:
        env_file = "../.env"


settings = Settings()

logger = getLogger(__name__)
