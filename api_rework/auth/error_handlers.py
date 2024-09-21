from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .errors import InsufficientPermissionsError, TokenDecodingError, TokenExpiredError
from starlette.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST


def include_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(InsufficientPermissionsError)
    def handle_insufficient_permissions_error(request: Request, exc: InsufficientPermissionsError):
        return JSONResponse(
            {"error_msg": str(exc)},
            status_code=HTTP_403_FORBIDDEN
        )

    @app.exception_handler(TokenDecodingError)
    def handle_invalid_token_error(request: Request, exc: TokenDecodingError):
        return JSONResponse(
            {"error_msg": "Token cannot be decoded"},
            status_code=HTTP_400_BAD_REQUEST
        )

    @app.exception_handler(TokenExpiredError)
    def handle_expired_token_error(request: Request, exc: TokenExpiredError):
        return JSONResponse(
            {"error_msg": "Token expired"},
            status_code=HTTP_403_FORBIDDEN
        )
