from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from .errors import (
    InsufficientPermissionsError,
    InvalidTokenError,
    TokenDecodingError,
    TokenExpiredError,
)


def include_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(InsufficientPermissionsError)
    def handle_insufficient_permissions_error(
        request: Request, exc: InsufficientPermissionsError
    ):
        return JSONResponse({"detail": str(exc)}, status_code=HTTP_403_FORBIDDEN)

    @app.exception_handler(TokenDecodingError)
    def handle_invalid_token_error(request: Request, exc: TokenDecodingError):
        return JSONResponse({"detail": str(exc)}, status_code=HTTP_400_BAD_REQUEST)

    @app.exception_handler(TokenExpiredError)
    def handle_expired_token_error(request: Request, exc: TokenExpiredError):
        return JSONResponse({"detail": str(exc)}, status_code=HTTP_403_FORBIDDEN)

    @app.exception_handler(InvalidTokenError)
    def handle_invalid_token(request: Request, exc: InvalidTokenError):
        return JSONResponse({"detail": str(exc)}, status_code=HTTP_403_FORBIDDEN)
