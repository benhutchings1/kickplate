import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DEBUG_MODE: bool = Field()
    CLUSTER_HOST: str = Field()
    CLUSTER_SERVICE_ACCOUNT_SECRET: str = Field()
    CLUSTER_CERTIFICATE_PATH: str = Field(default="certs/ca.crt")

    AUTH_TOKEN_URL: str = Field()
    AUTH_AUTH_URL: str = Field()
    AUTH_OIDC_CONFIG_URL: str = Field()
    AUTH_ISSUER: str = Field()
    AUTH_AUDIENCE: str = Field()
    AUTH_REQUIRED_ROLES: list[str] = os.environ["AUTH_REQUIRED_ROLES"].split(",")
    AUTH_CLIENT_ID: str = Field()


settings = Settings()
