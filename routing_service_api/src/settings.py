from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    storage1_url: str = Field("http://localhost:9000/", env="STORAGE1_URL")
    storage1_access_key: str = Field("admin")
    storage1_secret_key: str = Field("supersecret")
    storage1_ip: str = Field("83.220.236.105")

    storage2_url: str = Field("http://localhost:9003/", env="STORAGE2_URL")
    storage2_access_key: str = Field("admin")
    storage2_secret_key: str = Field("supersecret")
    storage2_ip: str = Field("95.142.196.32")

    storage3_url: str = Field("http://localhost:9005/", env="STORAGE2_URL")
    storage3_access_key: str = Field("admin")
    storage3_secret_key: str = Field("supersecret")
    storage3_ip: str = Field("92.255.196.137")

    bucket: str = Field("test")
    storages_count = 1

    class Config:
        env_file = "../.env"


settings = Settings()
