import logging

from minio import Minio
from minio.error import S3Error
from urllib3.exceptions import HTTPError

from core.config import settings


class LoaderException(Exception):
    pass


class MinioLoader:
    source_minio: Minio
    destination_minio: Minio
    part_size = 10 * 1024 * 1024
    parallel_uploads = 3

    def __init__(self, source_host: str, destination_host: str, access_key: str, secret_key: str):
        self.source_minio = Minio(source_host, access_key=access_key, secret_key=secret_key, secure=False)
        self.destination_minio = Minio(destination_host, access_key=access_key, secret_key=secret_key, secure=False)

    def copy_file(
        self, source_bucket: str, source_object: str, destination_bucket: str, destination_object: str
    ) -> dict:
        # 1 Получаем объект
        try:
            response = self.source_minio.get_object(source_bucket, source_object)
            size = int(response.info()["Content-Length"])
        except S3Error as err:
            logging.error(err)
            # return
            raise LoaderException(err)

        try:
            # 2 создаем bucket если его нет
            found = self.destination_minio.bucket_exists(destination_bucket)
            if not found:
                self.destination_minio.make_bucket(destination_bucket)
                logging.debug("Create new bucket: [{0}]".format(destination_bucket))

            # 3 Копируем данные
            result = self.destination_minio.put_object(
                destination_bucket,
                destination_object,
                data=response,
                length=size,
                num_parallel_uploads=self.parallel_uploads,
                part_size=self.part_size,
            )

        except HTTPError as err:
            logging.error(err)
            raise LoaderException(err)

        finally:
            response.close()
            response.release_conn()

        logging.debug(
            "created {0} object; etag: {1}, version-id: {2}".format(result.object_name, result.etag, result.version_id)
        )
        return {"name": result.object_name, "etag": result.etag, "size": size}

    def list_source_buckets(self) -> list[dict]:
        buckets = self.source_minio.list_buckets()
        return [{"name": bucket.name, "created_at": bucket.creation_date} for bucket in buckets]

    def list_destination_buckets(self) -> list[dict]:
        buckets = self.destination_minio.list_buckets()
        return [{"name": bucket.name, "created_at": bucket.creation_date} for bucket in buckets]

    def check_source(self) -> bool:
        try:
            self.list_source_buckets()
        except HTTPError:
            return False

        return True

    def check_destination(self) -> bool:
        try:
            self.list_destination_buckets()
        except HTTPError:
            return False

        return True


def copy_file(file_name: str, source: str, destination: str) -> dict:
    loader = MinioLoader(source, destination, settings.ACCESS_KEY, settings.SECRET_KEY)
    if not loader.check_source():
        return {"error": "source check error"}

    if not loader.check_destination():
        return {"error": "destination check error"}

    try:
        result = loader.copy_file(settings.BUCKET, file_name, settings.BUCKET, file_name)
    except LoaderException as err:
        return {"error": str(err)}

    return result


def delete_file(file_name: str, storage: str) -> dict:
    minio = Minio(storage, access_key=settings.ACCESS_KEY, secret_key=settings.SECRET_KEY, secure=False)
    try:
        # Ругнется если не будет файла.
        minio.stat_object(settings.BUCKET, file_name)

        # А удаление без наличия файла нормально проходит, можно много раз удалить))
        minio.remove_object(settings.BUCKET, file_name)

    except S3Error as err:
        return {"error": str(err)}

    return {"result": "deleted", "name": file_name, "storage": storage}
