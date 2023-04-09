import random
from operator import attrgetter

import httpx
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import async_session
from app.schemas import Film, FilmSync, Movie, SyncTask, UploadTask
from app.services.film_service import film_service
from app.services.s3storage_service import s3storage_service


async def random_films_score(session: AsyncSession) -> list[FilmSync]:
    films = await film_service.read_multi(session)
    films = [FilmSync(id=film.id, size_bytes=film.size_bytes, score=random.random()) for film in films]
    return films


def make_sync_task(
    film_scores: list[FilmSync], stored_films: list[Film], storage_size: int, free_space_limit: int
) -> SyncTask:
    film_scores.sort(key=attrgetter("score"), reverse=True)
    film_ids_to_store = set()
    free_space = storage_size
    for film in film_scores:
        free_space -= film.size_bytes
        if free_space < free_space_limit:
            break
        film_ids_to_store.add(film.id)

    stored_film_ids = {film.id for film in stored_films}

    film_ids_to_upload = film_ids_to_store - stored_film_ids
    film_ids_to_delete = stored_film_ids - film_ids_to_store

    master_url = settings.S3_MASTER_URL
    to_delete = [Movie(movie_id=film_id) for film_id in film_ids_to_delete]
    to_upload = [UploadTask(movie_id=film_id, storage_url=master_url) for film_id in film_ids_to_upload]
    return SyncTask(delete=to_delete, upload=to_upload)


async def send_sync_task(storage_ip: str):
    async with async_session() as session:
        # предполагаем, что есть сервис аналитики, который дает прогноз по
        # популярности фильмов, сейчас берем случайные значения популярности
        films_with_scores = await random_films_score(session)
        storage = await s3storage_service.get_storage_by_ip(session, storage_ip)
        films_in_storage = await film_service.get_films_by_storage(session, storage.url)

    task = make_sync_task(films_with_scores, films_in_storage, storage.size_bytes, settings.S3_FREE_SPACE_LIMIT)
    async with httpx.AsyncClient() as client:
        await client.post(f"{storage.url}{settings.SYNC_HTTP_PATH}", json=jsonable_encoder(task))
