from faker import Faker
from fastapi import FastAPI

from src.storages import StorageWorker

app = FastAPI(
    docs_url="/media/openapi",
    openapi_url="/media/openapi.json",
)

fake = Faker()

storage_worker = StorageWorker()


async def get_storage_worker():
    if storage_worker.cdn_storages:
        yield storage_worker
    await storage_worker.create_storage_list()
    yield storage_worker
