from celery import Celery
from celery.utils.log import get_task_logger

from core.config import settings
from core.s3 import copy_file, delete_file, load_file_to_storage

#   Celery
celery = Celery("tasks", broker=settings.CELERY_BROKER_URI, backend=settings.CELERY_BACKEND_URI)

# Create a logger - Enable to display the message on the task logger
celery_log = get_task_logger(__name__)


class TaskFailure(Exception):
    pass


# Create an order - run asynchronous with celery
#
@celery.task(name="MinioUpload")
def load_object(file_name: str, source: str, destination: str) -> dict[str, str]:
    result = copy_file(file_name, source, destination)

    if "error" in result:
        raise TaskFailure(result)

    return result


@celery.task(name="MinioDelete")
def delete_object(file_name: str, storage: str) -> dict[str, str]:
    result = delete_file(file_name, storage)

    if "error" in result:
        raise TaskFailure(result)

    return result


@celery.task(name="UploadFileToStorage")
def load_object_to_storage(file_path: str, object_name: str, storage: str):
    result = load_file_to_storage(file_path, object_name, storage)

    if "error" in result:
        raise TaskFailure(result)

    return result
