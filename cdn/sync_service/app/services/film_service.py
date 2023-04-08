from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Film, S3Storage
from app.schemas import FilmCreate, FilmUpdate
from app.services.crud_base import CRUDBase


class FilmService(CRUDBase[Film, FilmCreate, FilmUpdate]):
    async def add_film_to_storage(
        self,
        session: AsyncSession,
        film_id: UUID,
        film_size_bytes: int,
        storage: S3Storage,
    ) -> Film | None:
        result = await session.execute(
            select(self.model).filter(self.model.id == film_id).options(selectinload(self.model.storages))
        )
        film = result.scalar_one_or_none()
        if film:
            film.storages.append(storage)
        else:
            film = self.model(id=film_id, size_bytes=film_size_bytes, storages=[storage])
            session.add(film)

        await session.commit()
        return film

    async def delete_film_from_storage(
        self,
        session: AsyncSession,
        film_id: UUID,
        storage: S3Storage,
    ) -> Film | None:
        result = await session.execute(
            select(self.model).filter(self.model.id == film_id).options(selectinload(self.model.storages))
        )
        film = result.scalar_one()
        film.storages.remove(storage)
        await session.commit()
        return film


film_service = FilmService(Film)
