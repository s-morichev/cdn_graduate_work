from pydantic import BaseModel, BaseSettings, Field, root_validator, validator


class S3Settings(BaseModel):
    id: str
    url: str
    size: int
    ip: str


class Settings(BaseSettings):
    DEBUG: bool = Field(True, env="SYNC_DEBUG")
    S3_SETTINGS: list[S3Settings] = Field(..., env="SYNC_S3_HOSTS")
    S3_MASTER_ID: str = Field("master", env="SYNC_S3_MASTER_ID")
    S3_FREE_SPACE_LIMIT: int = Field(..., env="SYNC_S3_FREE_SPACE_LIMIT")
    SYNC_HTTP_PATH: str = "/api/v1/sync"
    SQLALCHEMY_DATABASE_URI: str = Field(
        ...,
        env="PG_SYNC_DSN",
    )

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def replace_scheme_to_async(cls, v: str) -> str:
        return v.replace("postgresql://", "postgresql+asyncpg://")


settings = Settings()
