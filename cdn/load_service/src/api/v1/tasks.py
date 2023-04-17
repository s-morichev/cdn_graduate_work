from celery.result import AsyncResult
from fastapi import APIRouter, Body

from core.core_model import CoreModel
from workers.worker import celery, delete_object, load_object, load_object_to_storage

router = APIRouter()


class LoadTask(CoreModel):
    file: str
    source: str
    destination: str


class UploadTask(CoreModel):
    file_path: str
    object_name: str
    storage: str


class DeleteTask(CoreModel):
    file: str
    storage: str


class ResponseTask(CoreModel):
    task_id: str


class ResponseStatus(CoreModel):
    task_id: str
    task_status: str
    task_result: str


load_examples = {
    "load pic": {
        "summary": "load picture",
        "value": LoadTask(file="P1010043.JPG", source="localhost:9000", destination="localhost:19000").json(),
    }
}

upload_to_storage_examples = {
    "load file": {
        "summary": "load file",
        "value": UploadTask(
            file_path='/home/data/media/piano.mp3', object_name='piano.mp3', storage="localhost:19000").json(),
    }
}

response_add_example = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "example task id": {"value": ResponseTask(task_id="82cdb1f0-1b1a-4da8-acde-83f08dffb703").json()}
                }
            }
        },
    }
}

status_example = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "example task status": {
                        "value": ResponseStatus(
                            task_id="82cdb1f0-1b1a-4da8-acde-83f08dffb703",
                            task_status="SUCCESS",
                            task_result=str(
                                {"name": "P1010043.JPG", "etag": "af45e05f6ccf09f776e038d4a70a34c9", "size": 2981355}
                            ),
                        ).json()
                    }
                }
            }
        },
    }
}


@router.post("/tasks/upload", response_model=ResponseTask, responses=response_add_example)
def add_task_upload(task: LoadTask = Body(..., examples=load_examples)):
    new_task = load_object.delay(task.file, task.source, task.destination)
    return ResponseTask(task_id=new_task.id)


@router.post("/tasks/delete", response_model=ResponseTask)
def add_task_delete(task: DeleteTask):
    new_task = delete_object.delay(task.file, task.storage)
    return ResponseTask(task_id=new_task.id)


@router.get("/tasks/status/{task_id}", response_model=ResponseStatus, responses=status_example)
def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery)
    return ResponseStatus(task_id=task_id, task_status=task_result.status, task_result=str(task_result.result))


@router.post("/tasks/upload_file_to_storage", response_model=ResponseTask, responses=response_add_example)
def add_task_upload_to_master(task: UploadTask = Body(..., examples=upload_to_storage_examples)):
    new_task = load_object_to_storage.delay(task.file_path, task.object_name, task.storage)
    return ResponseTask(task_id=new_task.id)
