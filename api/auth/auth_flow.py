from typing import Coroutine, Any, List
from fastapi.security import OAuth2AuthorizationCodeBearer
from auth.validator import TokenValidator
from fastapi import Request
from com_utils.error_handling import CustomError, HttpCodes
from com_utils.logger import LoggingLevel, Loggers
from config import ApiSettings


class OAuthCodeFlow(OAuth2AuthorizationCodeBearer):
    def __init__(
        self,
        authorizationUrl: str,
        tokenUrl: str,
        scheme_name: str,
        scopes: dict[str, str],
        description: str,
    ) -> None:
        super().__init__(
            authorizationUrl=authorizationUrl,
            tokenUrl=tokenUrl,
            scheme_name=scheme_name,
            scopes=scopes,
            description=description,
        )
        self.whitelisted_routes = [
            "/",  # Health check
            "/docs",  # Swagger docs
            "/openapi.json",  # Swagger docs requirements
            "/favicon.ico",  # Favicon
            "/docs/oauth2-redirect",  # swagger auth
        ]
        self.token_validator = TokenValidator()

    async def __call__(self, request: Request) -> Coroutine[Any, Any, str | None]:
        if not ApiSettings.auth_enable:
            return super().__call__(request)

        # Check if path is whitelisted
        if request.scope["path"] in self.whitelisted_routes:
            return super().__call__(request)

        # Check headers for bearer token authorisation
        if "authorization" not in request.headers:
            raise CustomError(
                error_code=HttpCodes.USER_UNAUTHORISED,
                message="Bearer token required",
                logging_message=f"IP: {request.client.host} tried to access \
                    {request.scope['path']} without a token",
                logging_level=LoggingLevel.INFO,
                logger=Loggers.SECURITY,
            )
        token = str(request.headers["authorization"]).split(" ")[1]
        token_contents = self.token_validator.verify_token(token=token)

        # Check group membership
        if ApiSettings.auth_group_id not in token_contents["groups"]:
            raise CustomError(
                error_code=HttpCodes.USER_UNAUTHORISED,
                message="User not member of security group",
                logging_message=f"IP: {request.client.host} tried to access \
                    {request.scope['path']} but isn't a member",
                logging_level=LoggingLevel.INFO,
                logger=Loggers.SECURITY,
            )

        return super().__call__(request)


oauth_scheme = OAuthCodeFlow(
    authorizationUrl=ApiSettings.authorize_endpoint,
    tokenUrl=ApiSettings.auth_token_endpoint,
    scheme_name="Deployment Engine",
    scopes={scope: scope for scope in ApiSettings.auth_group_id.split(" ")},
    description="Perform OAuth Authorisation Code with PKCE flow",
)
