import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
