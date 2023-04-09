from pydantic import BaseModel, BaseSettings, Field, root_validator, validator


class S3Settings(BaseModel):
    url: str
    size: int
    ip: str


class Settings(BaseSettings):
    DEBUG: bool = Field(True, env="SYNC_DEBUG")
    S3_SETTINGS: list[S3Settings] = Field(..., env="SYNC_S3_HOSTS")
    S3_MASTER_URL: str = None
    S3_FREE_SPACE_LIMIT: int = Field(..., env="SYNC_S3_FREE_SPACE_LIMIT")
    SYNC_HTTP_PATH: str = "/api/v1/sync"
    SQLALCHEMY_DATABASE_URI: str = Field(
        ...,
        env="PG_SYNC_DSN",
    )

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def replace_scheme_to_async(cls, v: str) -> str:
        return v.replace("postgresql://", "postgresql+asyncpg://")

    @root_validator
    def set_master_storage_url(cls, values):
        master_settings = values.get("S3_SETTINGS")[0]
        values["S3_MASTER_URL"] = master_settings.url
        return values


settings = Settings()
