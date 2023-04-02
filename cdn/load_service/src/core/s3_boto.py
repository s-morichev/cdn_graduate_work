import logging

# from minio import Minio
# from minio.error import S3Error
import boto3
from boto3.resources.base import ServiceResource
from boto3.s3.transfer import TransferConfig
from botocore.client import Config
from botocore.exceptions import ClientError, ConnectionError
from urllib3.exceptions import HTTPError

from core.config import settings


class LoaderException(Exception):
    pass


class MinioLoader:
    source_storage = None
    destination_storage = None
    part_size = 10 * 1024 * 1024
    parallel_uploads = 3

    def __init__(self, source_host: str, destination_host: str, access_key: str, secret_key: str):
        config = Config(signature_version="s3v4")
        self.source_storage = boto3.resource(
            "s3",
            endpoint_url=f"http://{source_host}",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=config,
        )

        self.destination_storage = boto3.resource(
            "s3",
            endpoint_url=f"http://{destination_host}",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=config,
        )
        # self.source_minio = Minio(source_host, access_key=access_key, secret_key=secret_key, secure=False)
        # self.destination_minio = Minio(destination_host, access_key=access_key, secret_key=secret_key, secure=False)

    def copy_file(
        self, source_bucket: str, source_object: str, destination_bucket: str, destination_object: str
    ) -> dict:
        # 1 Получаем объект
        try:
            obj = self.source_storage.Bucket(source_bucket).Object(key=source_object)
            print(type(obj))
            size = obj.content_length
        except (ClientError, ConnectionError) as error:
            logging.error(error)
            # return
            raise LoaderException(error)

        print(obj)
        print(size)

        # 2 пытаемся создать Bucket - так все в одну команду сервера получается
        try:
            self.destination_storage.Bucket(destination_bucket)

        except ClientError as error:
            if error.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
                logging.debug("Bucket %s already exists! Using it.", destination_bucket)
            else:
                logging.exception("Couldn't create bucket %s.", destination_bucket)
                raise LoaderException(error)

        # 3 Загружаем
        config = TransferConfig(multipart_chunksize=self.part_size)

        # transfer = boto3.s3.transfer.MultipartDownloader
        response = self.destination_storage.Bucket(destination_bucket).put_object(
            Key=destination_object, Body=obj.get()["Body"].read()
        )
        logging.debug(
            "created {0} object; etag: {1}, version-id: {2}".format(
                destination_object, response.e_tag, response.version_id
            )
        )
        return {"name": destination_object, "etag": response.e_tag, "size": size}

    def copy_file2(
        self, source_bucket: str, source_object: str, destination_bucket: str, destination_object: str
    ) -> dict:
        # 1 Получаем объект
        try:
            obj = self.source_storage.Bucket(source_bucket).Object(key=source_object)
            print(type(obj))
            size = obj.content_length
        except (ClientError, ConnectionError) as error:
            logging.error(error)
            # return
            raise LoaderException(error)

        print(obj)
        print(size)

        # 2 пытаемся создать Bucket - так все в одну команду сервера получается
        try:
            self.destination_storage.Bucket(destination_bucket)

        except ClientError as error:
            if error.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
                logging.debug("Bucket %s already exists! Using it.", destination_bucket)
            else:
                logging.exception("Couldn't create bucket %s.", destination_bucket)
                raise LoaderException(error)

        # 3 Загружаем
        config = TransferConfig(multipart_chunksize=self.part_size)

        # transfer = boto3.s3.transfer.MultipartDownloader
        response = self.source_storage.meta.client.download_file(source_bucket, source_object, "tempory", Config=config)
        print('load ', response)
        response = self.destination_storage.meta.client.upload_file(
            "tempory", destination_bucket, destination_object, Config=config
        )
        print('upload ', response)
        return {'file': destination_object}
        # logging.debug(
        #     "created {0} object; etag: {1}, version-id: {2}".format(destination_object,
        #                                                             response.e_tag,
        #                                                             response.version_id)
        # )
        # return {"name": destination_object, "etag": response.e_tag, "size": size}

    def check_source(self) -> bool:
        try:
            self.source_storage.meta.client.head_bucket(Bucket="movies")
        except ConnectionError:
            return False

        except ClientError:
            pass

        return True

    def check_destination(self) -> bool:
        try:
            self.destination_storage.meta.client.head_bucket(Bucket="movies")

        except ConnectionError:
            return False

        except ClientError:
            pass

        return True


def copy_file(file_name: str, source: str, destination: str) -> dict[str, str]:
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


def delete_file(file_name: str, storage: str) -> dict[str, str]:
    minio = Minio(storage, access_key=settings.ACCESS_KEY, secret_key=settings.SECRET_KEY, secure=False)
    try:
        # Ругнется если не будет файла.
        minio.stat_object(settings.BUCKET, file_name)

        # А удаление без наличия файла нормально проходит, можно много раз удалить))
        minio.remove_object(settings.BUCKET, file_name)

    except S3Error as err:
        return {"error": str(err)}

    return {"result": "deleted", "name": file_name, "storage": storage}
