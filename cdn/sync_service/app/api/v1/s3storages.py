from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.services.s3storage_service import s3storage_service

router = APIRouter()


@router.get("", response_model=list[schemas.S3Storage])
async def read_multiple_storages(session: AsyncSession = Depends(deps.get_session)):
    s3storages = await s3storage_service.read_multi(session)
    return s3storages


@router.post("", response_model=schemas.S3Storage, status_code=HTTPStatus.CREATED)
async def create_storage(
    s3storage_in: schemas.S3StorageCreate,
    session: AsyncSession = Depends(deps.get_session),
):
    s3storage = await s3storage_service.create(session, obj_in=s3storage_in)
    return s3storage


@router.get("/{s3storage_id}", response_model=schemas.S3Storage)
async def read_storage(s3storage_id: str, session: AsyncSession = Depends(deps.get_session)):
    s3storage = await s3storage_service.read(session, id=s3storage_id)
    if not s3storage:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="S3 Storage not found")
    return s3storage


@router.patch("/{s3storage_id}")
async def update_storage(
    s3storage_id: str,
    s3storage_in: schemas.S3StorageUpdate,
    session: AsyncSession = Depends(deps.get_session),
):
    s3storage = await s3storage_service.read(session, id=s3storage_id)
    if not s3storage:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="S3 Storage not found")
    s3storage = await s3storage_service.update(session, db_obj=s3storage, obj_in=s3storage_in)
    return s3storage


@router.delete("/{s3storage_id}")
async def delete_storage(
    s3storage_id: str,
    session: AsyncSession = Depends(deps.get_session),
):
    s3storage = await s3storage_service.delete(session, id=s3storage_id)
    if not s3storage:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="S3 Storage not found")
    return s3storage
