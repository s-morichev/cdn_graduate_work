from uuid import uuid4

from sqlalchemy import BigInteger, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class S3Storage(Base):
    __tablename__ = "s3storages"
    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    url: Mapped[str] = mapped_column(String(255), unique=True)
    ip_address: Mapped[str] = mapped_column(String(255), unique=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self):
        return f"<S3Storage {self.url}>"


class FilmS3Storage(Base):
    __tablename__ = "films_s3storages"
    film_id: Mapped[Uuid] = mapped_column(ForeignKey("films.id", ondelete="CASCADE"), primary_key=True)
    s3storage_id: Mapped[Uuid] = mapped_column(ForeignKey("s3storages.id", ondelete="CASCADE"), primary_key=True)


class Film(Base):
    __tablename__ = "films"
    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self):
        return f"<Film {self.id}>"
