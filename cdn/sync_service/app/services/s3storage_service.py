from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import FilmS3Storage, S3Storage
from app.schemas import S3StorageCreate, S3StorageUpdate
from app.services.crud_base import CRUDBase


class S3StorageService(CRUDBase[S3Storage, S3StorageCreate, S3StorageUpdate]):
    async def read_multi_by_film(self, session: AsyncSession, *, film_id: UUID) -> list[S3Storage]:
        result = await session.scalars(
            select(self.model)
            .join(
                FilmS3Storage,
            )
            .filter(FilmS3Storage.film_id == film_id)
        )
        return result.all()


s3storage_service = S3StorageService(S3Storage)
