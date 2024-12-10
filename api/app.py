import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer

from auth.validator import initialise_token_validator
from error_handling import add_error_handlers
from features.graph.router import router as graph_router
from features.health.router import router as health_router
from settings import settings

logger = logging.Logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    logger.info("Fetching OIDC config...")
    initialise_token_validator()
    logger.info("...Fetched OIDC config")

    yield


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.AUTH_AUTH_URL,
    tokenUrl=settings.AUTH_TOKEN_URL,
)

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_init_oauth={
        "clientId": settings.AUTH_CLIENT_ID,
        "scopes": "",
        "appName": "Kickplate API",
        "userPkceWithAuthorizationCodeGrant": True,
    },
)

add_error_handlers(app)
app.include_router(health_router)
app.include_router(graph_router)

if __name__ == "__main__":
    if settings.DEBUG_MODE:
        uvicorn.run("app:app", host="localhost", port=8080, reload=True)
