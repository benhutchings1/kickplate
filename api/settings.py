from pydantic import Field
from pydantic_settings import BaseSettings

from models.auth import Role


class Settings(BaseSettings):
    DEBUG_MODE: bool = Field()
    AUTH_TOKEN_URL: str = Field()
    AUTH_AUTH_URL: str = Field()
    AUTH_OIDC_CONFIG_URL: str = Field()
    AUTH_ISSUER: str = Field()
    AUTH_AUDIENCE: str = Field()
    AUTH_REQUIRED_ROLE: Role = Field()
    AUTH_CLIENT_ID: str = Field()


settings = Settings()
