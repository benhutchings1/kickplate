import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

_LOGGER = logging.getLogger(__name__)


class BaseGraphExceptions(Exception):
    """Base exception for all graph errors"""

    pass


class UndeterminedApiError(BaseGraphExceptions):
    """API Error could not be categorised"""

    pass


class EDAGAlreadyExistsError(BaseGraphExceptions):
    """User tried to create an edag which already existed"""

    def __init__(self, edag_name: str):
        self.edag_name = edag_name
        super().__init__(f"An EDAG with name {edag_name} already exists")


class EDAGNotFoundError(BaseGraphExceptions):
    def __init__(self, edag_name: str):
        self.edag_name = edag_name
        super().__init__(f"EDAG {edag_name} not found")


def add_exception_handlers(app) -> None:
    @app.exception_handler(UndeterminedApiError)
    def handle_unknown_api_error(request: Request, exc: UndeterminedApiError):
        _LOGGER.error("Unknown error", exc_info=exc)
        return JSONResponse(
            {
                "detail": "An unknown error occured, please try again or contact an admin"
            },
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(EDAGAlreadyExistsError)
    def handle_edag_already_exists(request: Request, exc: EDAGAlreadyExistsError):
        return JSONResponse(
            {"detail": str(exc)},
            status_code=HTTP_409_CONFLICT,
        )

    @app.exception_handler(EDAGNotFoundError)
    def handle_edag_not_found(request: Request, exc: EDAGNotFoundError):
        return JSONResponse(
            {"detail": str(exc)},
            status_code=HTTP_404_NOT_FOUND,
        )
