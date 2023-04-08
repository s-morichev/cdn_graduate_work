from uuid import UUID

import requests
import uvicorn
from faker import Faker
from fastapi import FastAPI, Depends, HTTPException
from fastapi import Request

from src.jwt_config import AccessTokenPayload, jwt_bearer
from src.storages import ObjectStorageBase, StorageWorker
from src.settings import settings

app = FastAPI()

fake = Faker()


@app.get("/get_media/{obj_name}")
async def get_media(request: Request, obj_name: str | UUID,
                    token_payload: AccessTokenPayload = Depends(jwt_bearer),
                    ):
    user_id = str(token_payload.sub)
    try:
        requests.post(f"{settings.ugc_service_url}/api/v1/record_film/{user_id}")
    # TODO: обработать ошибку
    except Exception:
        pass
    if request.client.host == "127.0.0.1":
        ip_address = fake.ipv4()
    else:
        ip_address = request.client.host
    storages = await storage_worker.get_storages(ip_address)

    for storage_info in storages:
        storage = storage_info.get("storage")
        if not storage:
            continue
        cdn = ObjectStorageBase(endpoint_url=storage.url,
                                access_key=storage.access_key,
                                secret_key=storage.secret_key,
                                bucket=settings.bucket
                                )
        if cdn.check_file(obj_name):
            url = cdn.get_link_file(obj_name)
            return {"ip_address": ip_address, "storage": storage.url, "url": url}
    return HTTPException(status_code=404, detail="file not found")


if __name__ == "__main__":
    storage_worker = StorageWorker()
    storage_worker.create_storage_list()
    uvicorn.run(app, host="127.0.0.1", port=8001)
