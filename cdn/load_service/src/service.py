from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.ping import router as ping_router
from api.v1.tasks import router as task_router
from core.config import settings

# Create a FASTAPI application

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", default_response_class=ORJSONResponse)

app.include_router(task_router, prefix="/v1", tags=["Tasks"])
app.include_router(ping_router, prefix="", tags=["Ping"])
