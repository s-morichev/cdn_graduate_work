import boto3
import botocore.exceptions
import geocoder
import requests
from geopy.distance import distance
from requests.exceptions import ConnectionError

from src.schemas import Storage
from src.settings import settings, logger


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

        # Пока сам создаю ведра, в будущем выпилить
        try:
            self.s3.create_bucket(Bucket=self.bucket)
        except botocore.exceptions.ClientError:
            logger.info('Bucket already exists')

    def check_file(self, key):
        try:
            obj = self.s3.head_object(Bucket=self.bucket, Key=key)
            return obj
        except botocore.exceptions.ClientError:
            logger.info('Object does not exist')
            return

    def get_link_file(self, key):
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': key
            },
            ExpiresIn=3600 * 24  # set expiration time for 24 hour
        )
        return url


def get_example_storages():
    # Пример получения списка хранилищ из сервиса синхронизации
    return [
        {"url": "http://localhost:9000/", "ip_address": "83.220.236.105"},
        {"url": "http://localhost:90010/", "ip_address": "95.142.196.32"},
        {"url": "http://localhost:90020/", "ip_address": "92.255.196.137"}
    ]


class StorageWorker:
    cdn_storages = []

    def create_storage_list(self):
        try:
            storages = requests.get(f"{settings.sync_service_url}/get_storages")
            storages = storages.json()
        except ConnectionError:
            logger.error("Sync service is not available")
            storages = get_example_storages()
            # return
        for storage in storages:
            self.cdn_storages.append(
                Storage(
                    url=storage["url"],
                    ip=storage["ip_address"],
                    access_key=settings.storage_access_key,
                    secret_key=settings.storage_secret_key
                ))

    async def get_storages(self, ip_address) -> list[dict]:
        user_geo = geocoder.ip(ip_address)
        storages = []
        for i in range(len(self.cdn_storages)):
            dist = distance(geocoder.ip(self.cdn_storages[i].ip).latlng, user_geo.latlng).km
            storages.append(
                {
                    "storage": self.cdn_storages[i],
                    "distance": dist
                }
            )
        storages.sort(key=lambda x: x["distance"])
        return storages
