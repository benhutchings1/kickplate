from unittest.mock import AsyncMock, Mock

import pytest
from httpx import AsyncClient

from app import app
from features.graph.exceptions import (
    EDAGAlreadyExistsError,
    EDAGNotFoundError,
    UndeterminedApiError,
)
from features.graph.services import EDAGServices
from models.edag import EDAGRequest
from models.edagrun import EDAGRunResponse

pytestmark = pytest.mark.asyncio


async def test_create_edag(
    async_client: AsyncClient, edag_request: EDAGRequest
) -> None:
    class MockEdagServices(EDAGServices):
        async def create_edag(self, request: EDAGRequest) -> None:
            assert request == edag_request

    app.dependency_overrides[EDAGServices] = MockEdagServices

    resp = await async_client.post(f"/api/v1/edag/", json=edag_request.model_dump())

    assert resp.status_code == 200


async def test_should_return_409_on_existing_edag(
    async_client: AsyncClient, edag_request: EDAGRequest
):
    class MockEdagServices(EDAGServices):
        async def create_edag(self, request: EDAGRequest) -> None:
            raise EDAGAlreadyExistsError(request.graphname)

    app.dependency_overrides[EDAGServices] = MockEdagServices

    resp = await async_client.post(f"/api/v1/edag/", json=edag_request.model_dump())

    assert resp.status_code == 409
    assert "detail" in resp.json()


async def test_should_return_500_on_unknown_error(
    async_client: AsyncClient, edag_request: EDAGRequest
):
    class MockEdagServices(EDAGServices):
        async def create_edag(self, request: EDAGRequest) -> None:
            raise UndeterminedApiError()

    app.dependency_overrides[EDAGServices] = MockEdagServices

    resp = await async_client.post(f"/api/v1/edag/", json=edag_request.model_dump())

    assert resp.status_code == 500
    assert "detail" in resp.json()


async def test_run_edag(async_client: AsyncClient, edag_run_response: EDAGRunResponse):
    class MockEdagServices(EDAGServices):
        async def run_edag(self, edagname: str) -> EDAGRunResponse:
            assert edagname == edag_name
            return edag_run_response

    app.dependency_overrides[EDAGServices] = MockEdagServices

    edag_name = "myedag"
    resp = await async_client.post(f"/api/v1/edag/{edag_name}/run")

    assert resp.status_code == 200
    assert resp.json()["id"] == edag_run_response.id


async def test_should_return_404_if_edag_not_found(async_client: AsyncClient):
    class MockEdagServices(EDAGServices):
        async def run_edag(self, edagname: str) -> EDAGRunResponse:
            raise EDAGNotFoundError(edagname)

    app.dependency_overrides[EDAGServices] = MockEdagServices

    edag_name = "myedag"
    resp = await async_client.post(f"/api/v1/edag/{edag_name}/run")

    assert resp.status_code == 404
    assert "detail" in resp.json()
