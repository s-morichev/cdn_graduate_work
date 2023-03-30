from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR.parent / ".env.local"


class Settings(BaseSettings):
    PROJECT_NAME: str = "S3 Load service"
    DEBUG: bool = Field(True, env="S3LS_DEBUG")
    CELERY_BROKER_URI = Field("amqp://guest:guest@127.0.0.1:5672//", env="S3LS_CELERY_BROKER_URI")
    CELERY_BACKEND_URI = Field("rpc", env="S3LS_CELERY_BACKEND_URI")
    BUCKET: str = "movies"
    ACCESS_KEY: str = Field(..., env="S3LS_ACCESS_KEY")
    SECRET_KEY: str = Field(..., env="S3LS_SECRET_KEY")


settings = Settings(_env_file=ENV_FILE)
