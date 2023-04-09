from uuid import UUID

from app.schemas.base_class import BaseSchema


class Movie(BaseSchema):
    movie_id: UUID


class UploadTask(BaseSchema):
    movie_id: UUID
    storage_url: str


class SyncTask(BaseSchema):
    delete: list[Movie]
    upload: list[UploadTask]
