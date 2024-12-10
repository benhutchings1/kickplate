from fastapi import FastAPI

from auth.error_handlers import include_error_handlers as auth_error_handlers


def add_error_handlers(app: FastAPI) -> None:
    auth_error_handlers(app)
