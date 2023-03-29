import uvicorn
from faker import Faker
from fastapi import FastAPI
from fastapi import Request
from geopy.distance import distance
import geocoder
from pydantic import BaseModel

from src.storages import ObjectStorageBase
from src.settings import settings

app = FastAPI()

cdn_storages = []


class Storage(BaseModel):
    url: str
    ip: str
    access_key: str
    secret_key: str


def create_storage_list():
    for i in range(1, settings.storages_count + 1):
        storage_url = getattr(settings, f"storage{i}_url")
        storage_access_key = getattr(settings, f"storage{i}_access_key")
        storage_secret_key = getattr(settings, f"storage{i}_secret_key")
        storage_ip = getattr(settings, f"storage{i}_ip")
        storage = Storage(
            url=storage_url,
            ip=storage_ip,
            access_key=storage_access_key,
            secret_key=storage_secret_key
        )
        cdn_storages.append(storage)


fake = Faker()


def get_cdn(ip_address):
    user_geo = geocoder.ip(ip_address)
    min_dist = distance(geocoder.ip(cdn_storages[0].ip).latlng, user_geo.latlng).km
    min_dist_index = 0
    for i in range(1, len(cdn_storages)):
        dist = distance(geocoder.ip(cdn_storages[i].ip).latlng, user_geo.latlng).km
        if dist < min_dist:
            min_dist = dist
            min_dist_index = i
    return cdn_storages[min_dist_index]


@app.get("/get_ip")
async def get_media(request: Request, obj_name):
    if request.client.host == "127.0.0.1":
        ip_address = fake.ipv4()
    else:
        ip_address = request.client.host
    storage = get_cdn(ip_address)
    cdn = ObjectStorageBase(endpoint_url=storage.url,
                            access_key=storage.access_key,
                            secret_key=storage.secret_key,
                            bucket=settings.bucket
                            )
    url = ""
    if cdn.check_file(obj_name):
        url = cdn.get_link_file(obj_name)
    return {"ip_address": ip_address, "storage": storage.url, "url": url}


if __name__ == "__main__":
    create_storage_list()
    uvicorn.run(app, host="127.0.0.1", port=8000)
