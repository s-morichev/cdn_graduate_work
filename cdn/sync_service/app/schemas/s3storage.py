from uuid import UUID

from pydantic import AnyHttpUrl, IPvAnyAddress

from app.schemas.base_class import BaseSchema


class S3StorageBase(BaseSchema):
    """Общие свойства схем."""

    url: AnyHttpUrl
    ip_address: IPvAnyAddress
    size_bytes: int


class S3StorageCreate(S3StorageBase):
    """Схема для создания."""

    pass


class S3StorageUpdate(BaseSchema):
    """Схема для обновления."""

    url: AnyHttpUrl | None = None
    ip_address: IPvAnyAddress | None = None
    size_bytes: int | None = None


class S3Storage(S3StorageBase):
    """Схема для возврата из API."""

    id: UUID
