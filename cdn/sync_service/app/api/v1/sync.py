from fastapi import APIRouter

from app.services.sync import send_sync_task

router = APIRouter()


@router.get("")
async def sync(storage_ip: str):
    await send_sync_task(storage_ip)
