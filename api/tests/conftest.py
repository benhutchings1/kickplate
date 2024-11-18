import pytest
from app import app
from httpx import ASGITransport, AsyncClient
from typing import AsyncIterable


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client() -> AsyncIterable[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
