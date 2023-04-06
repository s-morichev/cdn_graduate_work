from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.services.film_service import film_service
from app.services.s3storage_service import s3storage_service

router = APIRouter()


@router.post("", response_model=schemas.Film, status_code=HTTPStatus.CREATED)
async def create_film(
    film_in: schemas.FilmCreate,
    session: AsyncSession = Depends(deps.get_session),
):
    film = await film_service.create(session, obj_in=film_in)
    return film


@router.post("/event/create", status_code=HTTPStatus.CREATED)
async def create_film(
    request: Request,
    session: AsyncSession = Depends(deps.get_session),
):
    event = await request.json()
    import json

    print(json.dumps(event, indent=2))


@router.get("/{film_id}/storages", response_model=list[schemas.S3Storage])
async def read_film_storages(film_id: UUID, session: AsyncSession = Depends(deps.get_session)):
    s3storages = await s3storage_service.read_multi_by_film(session, id=film_id)
    return s3storages


@router.delete("/{film_id}")
async def delete_film(
    film_id: UUID,
    session: AsyncSession = Depends(deps.get_session),
):
    film = await film_service.delete(session, id=film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Film not found")
    return film
