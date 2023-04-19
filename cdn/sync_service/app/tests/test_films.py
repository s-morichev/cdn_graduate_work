from http import HTTPStatus
from urllib.parse import urlparse

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import add_storages
from app.tests import constants

pytestmark = pytest.mark.asyncio


async def test_put_events(client: AsyncClient, session: AsyncSession):
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
    master_url = constants.put_to_master_event["Records"][0]["responseElements"]["x-minio-origin-endpoint"]
    master_ip = urlparse(master_url).netloc.split(":")[0]
    edge_url = constants.put_to_edge_event["Records"][0]["responseElements"]["x-minio-origin-endpoint"]
    edge_ip = urlparse(edge_url).netloc.split(":")[0]

    response = await client.get(f"api/v1/films/{film_id}/storages")
    assert response.status_code == HTTPStatus.OK
    storage_ips = {storage["ip_address"] for storage in response.json()}
    assert storage_ips == {master_ip, edge_ip}
