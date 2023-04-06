import os

from pydantic import BaseSettings, Field, validator

print(os.getenv("PG_SYNC_DSN"))


class Settings(BaseSettings):
    DEBUG: bool = Field(True, env="SYNC_DEBUG")
    SQLALCHEMY_DATABASE_URI: str = Field(
        ...,
        env="PG_SYNC_DSN",
    )

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def replace_scheme_to_async(cls, v: str) -> str:
        return v.replace("postgresql://", "postgresql+asyncpg://")


settings = Settings()
