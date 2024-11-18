from pydantic_settings import BaseSettings
from typing import Optional


class _Settings(BaseSettings):
    DEBUG_MODE: bool = True
    CLUSTER_HOST: Optional[str] = None
    CLUSTER_SERVICE_ACCOUNT_SECRET: Optional[str] = None
    CLUSTER_CERTIFICATE_PATH: Optional[str] = None

    AUTH_JWKS_URL: Optional[str] = None
    AUTH_ISSUER: Optional[str] = None
    AUTH_AUDIENCE: Optional[str] = None


settings = _Settings()
