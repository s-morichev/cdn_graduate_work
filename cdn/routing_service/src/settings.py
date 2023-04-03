from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    storage1_url: str = Field("http://localhost:9000/", env="STORAGE1_URL")
    storage1_access_key: str = Field("admin", env="MINIO_USER")
    storage1_secret_key: str = Field("supersecret", env="MINIO_PASSWORD")
    storage1_ip: str = Field("83.220.236.105")

    storage2_url: str = Field("http://localhost:9010/", env="STORAGE2_URL")
    storage2_access_key: str = Field("admin", env="MINIO_USER")
    storage2_secret_key: str = Field("supersecret", env="MINIO_PASSWORD")
    storage2_ip: str = Field("95.142.196.32")

    storage3_url: str = Field("http://localhost:9020/", env="STORAGE3_URL")
    storage3_access_key: str = Field("admin", env="MINIO_USER")
    storage3_secret_key: str = Field("supersecret", env="MINIO_PASSWORD")
    storage3_ip: str = Field("92.255.196.137")

    bucket: str = Field("test", env="MOVIES_BUCKET")
    storages_count = 3

    class Config:
        env_file = "../.env"


settings = Settings()
