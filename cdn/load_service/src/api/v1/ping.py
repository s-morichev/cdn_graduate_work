from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from models.update import Actions
from workers.worker import add_result_notice

router = APIRouter()


@router.get("/ping")
async def ping():
    add_result_notice(Actions.DELETE, "test")
    return ORJSONResponse("pong")
