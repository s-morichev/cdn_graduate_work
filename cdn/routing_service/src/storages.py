import boto3

from geopy.distance import distance
import geocoder
from src.schemas import Storage

from src.settings import settings


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
        except Exception:
            pass

    def check_file(self, key):
        try:
            obj = self.s3.head_object(Bucket=self.bucket, Key=key)
            return obj
        except Exception:
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


class StorageWorker:
    cdn_storages = []

    def create_storage_list(self):
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
            self.cdn_storages.append(storage)

    def get_cdn(self, ip_address):
        user_geo = geocoder.ip(ip_address)
        min_dist = distance(geocoder.ip(self.cdn_storages[0].ip).latlng, user_geo.latlng).km
        min_dist_index = 0
        for i in range(1, len(self.cdn_storages)):
            dist = distance(geocoder.ip(self.cdn_storages[i].ip).latlng, user_geo.latlng).km
            if dist < min_dist:
                min_dist = dist
                min_dist_index = i
        return self.cdn_storages[min_dist_index]
