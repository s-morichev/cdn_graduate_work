import aiohttp
import backoff as backoff
import boto3
import botocore.exceptions
import geocoder
from geopy.distance import distance

from src.schemas import Storage
from src.settings import settings, logger


# при запуске в dev окружении в компоузе урлы хранилищ отличаются для внутренних
# юзеров (в компоузе) и внешних (на хосте)
# подменяем урл для генерации ссылок TODO сделать нормальную реализацию
change_urls = {
    "http://minio-0:9000": "http://localhost:9000",
    "http://minio-1:9000": "http://localhost:9010",
    "http://minio-2:9000": "http://localhost:9020",
}

change_ip = {
    "172.18.0.10": "109.252.76.233",  # Москва
    "172.18.0.11": "178.162.102.173",  # Санкт Петербург
    "172.18.0.12": "213.151.2.107",  # Екатеринбург
}


class ObjectStorageBase:

    def __init__(self, endpoint_url, access_key, secret_key, bucket):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
        # только для демонстрации работы в dev окружении
        url_for_links = change_urls.get(endpoint_url)
        if url_for_links:
            self.s3_for_links = boto3.client(
                's3',
                endpoint_url=url_for_links,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
        else:
            self.s3_for_links = self.s3

    def check_file(self, key):
        try:
            obj = self.s3.head_object(Bucket=self.bucket, Key=key)
            return obj
        except botocore.exceptions.ClientError:
            logger.info('Object does not exist')
            return

    def get_link_file(self, key):
        url = self.s3_for_links.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': key
            },
            ExpiresIn=3600 * 24  # set expiration time for 24 hour
        )
        return url


class StorageWorker:
    cdn_storages = []

    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=3)
    async def create_storage_list(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{settings.sync_service_url}/api/v1/storages", headers={"Authorization": settings.secret_key}
            ) as response:
                response.raise_for_status()
                storages = await response.json()
        for storage in storages:
            # подменяем для демонстрации
            ip_addr = change_ip.get(storage["ip_address"])
            if not ip_addr:
                ip_addr = storage["ip_address"]
            self.cdn_storages.append(
                Storage(
                    url=storage["url"],
                    ip=ip_addr,
                    access_key=settings.storage_access_key,
                    secret_key=settings.storage_secret_key
                ))

    async def get_storages(self, ip_address) -> list[dict]:
        user_geo = geocoder.ip(ip_address)
        storages = []
        if not self.cdn_storages:
            return storages
        for storage in self.cdn_storages:
            dist = distance(geocoder.ip(storage.ip).latlng, user_geo.latlng).km
            storages.append(
                {
                    "storage": ObjectStorageBase(
                        endpoint_url=storage.url,
                        access_key=storage.access_key,
                        secret_key=storage.secret_key,
                        bucket=settings.bucket
                    ),
                    "distance": dist
                }
            )
        storages.sort(key=lambda x: x["distance"])
        return storages
