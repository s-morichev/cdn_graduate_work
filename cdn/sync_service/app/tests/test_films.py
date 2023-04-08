from http import HTTPStatus

import pytest
import pytest_asyncio
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import add_storages
from app.models.models import S3Storage
from app.tests import constants

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def clear_s3storage_table(session: AsyncSession):
    await session.execute(delete(S3Storage))
    await session.commit()


async def test_events(client: AsyncClient, session: AsyncSession):
    await add_storages(session)
    response = await client.post(
        "api/v1/films/events",
        json=jsonable_encoder(constants.put_to_master_event),
    )
    assert response.status_code == HTTPStatus.OK
    response = await client.post(
        "api/v1/films/events",
        json=jsonable_encoder(constants.put_to_edge_event),
    )
    assert response.status_code == HTTPStatus.OK

    film_id = constants.put_to_master_event["Records"][0]["s3"]["object"]["key"]
    master_ip = constants.put_to_master_event["Records"][0]["source"]["host"]
    edge_ip = constants.put_to_edge_event["Records"][0]["source"]["host"]

    response = await client.get(f"api/v1/films/{film_id}/storages")
    assert response.status_code == HTTPStatus.OK
    storage_ips = {storage["ip_address"] for storage in response.json()}
    assert storage_ips == {master_ip, edge_ip}
