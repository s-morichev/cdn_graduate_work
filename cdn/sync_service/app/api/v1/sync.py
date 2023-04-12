from fastapi import APIRouter

from app.services.sync import send_sync_task

router = APIRouter()


@router.post("")
async def sync(storage_id: str):
    await send_sync_task(storage_id)
