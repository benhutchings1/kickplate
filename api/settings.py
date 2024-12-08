import os

from pydantic import BaseModel


class Settings(BaseModel):

    DEBUG_MODE: bool = os.environ["DEBUG_MODE"] == "true"
    CLUSTER_HOST: str = os.environ["CLUSTER_HOST"]
    CLUSTER_SERVICE_ACCOUNT_SECRET: str = os.environ["CLUSTER_SERVICE_ACCOUNT_SECRET"]
    CLUSTER_CERTIFICATE_PATH: str = os.environ["CLUSTER_CERTIFICATE_PATH"]

    AUTH_TOKEN_URL: str = os.environ["AUTH_TOKEN_URL"]
    AUTH_AUTH_URL: str = os.environ["AUTH_AUTH_URL"]
    AUTH_OIDC_CONFIG_URL: str = os.environ["AUTH_OIDC_CONFIG_URL"]
    AUTH_ISSUER: str = os.environ["AUTH_ISSUER"]
    AUTH_AUDIENCE: str = os.environ["AUTH_AUDIENCE"]
    AUTH_REQUIRED_ROLES: list[str] = os.environ["AUTH_REQUIRED_ROLES"].split(",")
    AUTH_CLIENT_ID: str = os.environ["AUTH_CLIENT_ID"]


settings = Settings()
