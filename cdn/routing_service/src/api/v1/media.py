from uuid import UUID

from fastapi import Depends, HTTPException, APIRouter
from fastapi import Request, status

from src.config import get_storage_worker
from src.jwt_config import AccessTokenPayload, jwt_bearer
from src.storages import StorageWorker
from src.utils import save_info_ugc_service, get_ip_address

router = APIRouter(prefix="/media", tags=["media"], responses={404: {"description": "Not found"}})


@router.get("/get_media/{obj_name}")
async def get_media(
        request: Request,
        obj_name: UUID,
        token_payload: AccessTokenPayload = Depends(jwt_bearer),
        storage_worker: StorageWorker = Depends(get_storage_worker)
):
    filename = str(obj_name)
    user_id = str(token_payload.sub)
    await save_info_ugc_service(obj_name, user_id)
    ip_address = await get_ip_address(request)
    storages = await storage_worker.get_storages(ip_address)
    if not storages:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="storages not found")
    for storage_info in storages:
        storage = storage_info.get("storage")
        if not storage:
            continue
        if storage.check_file(filename):
            url = storage.get_link_file(filename)
            return {"url": url}
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file not found")
