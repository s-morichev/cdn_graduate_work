import uvicorn
from faker import Faker
from fastapi import FastAPI
from fastapi import Request

from src.storages import ObjectStorageBase, StorageWorker
from src.settings import settings

app = FastAPI()

cdn_storages = []

fake = Faker()


@app.get("/get_ip")
async def get_media(request: Request, obj_name):
    if request.client.host == "127.0.0.1":
        ip_address = fake.ipv4()
    else:
        ip_address = request.client.host
    storage = storage_worker.get_cdn(ip_address)
    cdn = ObjectStorageBase(endpoint_url=storage.url,
                            access_key=storage.access_key,
                            secret_key=storage.secret_key,
                            bucket=settings.bucket
                            )
    if cdn.check_file(obj_name):
        url = cdn.get_link_file(obj_name)
    else:
        cdn = ObjectStorageBase(
            endpoint_url=settings.storage1_url,
            access_key=settings.storage1_access_key,
            secret_key=settings.storage1_secret_key,
            bucket=settings.bucket
        )
        url = cdn.get_link_file(obj_name)
    return {"ip_address": ip_address, "storage": storage.url, "url": url}


if __name__ == "__main__":
    storage_worker = StorageWorker()
    storage_worker.create_storage_list()
    uvicorn.run(app, host="127.0.0.1", port=8000)
