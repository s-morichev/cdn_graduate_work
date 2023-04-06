from app.models.models import Film
from app.schemas import FilmCreate, FilmUpdate
from app.services.crud_base import CRUDBase


class FilmService(CRUDBase[Film, FilmCreate, FilmUpdate]):
    pass


film_service = FilmService(Film)
