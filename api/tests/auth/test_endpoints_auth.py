from typing import cast
from fastapi import Response
from httpx import AsyncClient
import pytest
from starlette.routing import Route
from app import app
from auth.errors import (
    InsufficientPermissionsError,
    InvalidTokenError,
    TokenDecodingError,
)
from auth.security import RBACSecurity
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN


pytestmark = pytest.mark.asyncio


def get_app_routes() -> list[tuple[str, str]]:
    # Routes that dont require auth
    ignored_routes = [
        "/openapi.json",
        "/docs",
        "swagger_ui_html",
        "/docs/oauth2-redirect",
        "/redoc",
        "/health",
    ]
    testing_routes = []
    for route in app.routes:
        route = cast(Route, route)
        if route.path not in ignored_routes:
            for method in list(route.methods):  # type: ignore
                testing_routes.append((route.path, method))
    return testing_routes


@pytest.mark.parametrize("route", get_app_routes())
async def test_should_return_401_on_missing_token(
    route: tuple[str, str], auth_async_client: AsyncClient
):
    path = route[0]
    method = route[1]
    send_request_fn = getattr(auth_async_client, method.lower())

    resp: Response = await send_request_fn(path)

    assert resp.status_code == 401


async def test_should_return_403_on_missing_role(auth_async_client: AsyncClient):
    def raise_error():
        raise InsufficientPermissionsError(["role"])

    app.dependency_overrides[RBACSecurity.verify] = raise_error
    resp = await auth_async_client.post("/api/v1/edag/")
    assert resp.status_code == HTTP_403_FORBIDDEN


async def test_should_return_400_on_bad_token(auth_async_client: AsyncClient):
    def raise_error():
        raise TokenDecodingError()

    app.dependency_overrides[RBACSecurity.verify] = raise_error
    resp = await auth_async_client.post("/api/v1/edag/")
    assert resp.status_code == HTTP_400_BAD_REQUEST


async def test_should_return_400_on_invalid_token(auth_async_client: AsyncClient):
    def raise_error():
        raise InvalidTokenError()

    app.dependency_overrides[RBACSecurity.verify] = raise_error
    resp = await auth_async_client.post("/api/v1/edag/")
    assert resp.status_code == HTTP_403_FORBIDDEN
