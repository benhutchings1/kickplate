from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes

from models.auth import Role, TokenContents, User
from settings import settings

from .errors import InsufficientPermissionsError
from .validator import TokenValidator, get_token_validator

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.AUTH_AUTH_URL,
    tokenUrl=settings.AUTH_TOKEN_URL,
    scopes={
        "openid profile email": "Default scopes (openid, profile, email)",
    },
)


class OAuth:
    def __call__(
        self,
        access_token: Annotated[str, Depends(oauth2_scheme)],
        token_validator: Annotated[TokenValidator, Depends(get_token_validator)],
    ) -> User:
        token_contents: TokenContents = token_validator.decode_verify_token(
            access_token
        )
        return User(
            email=token_contents.email,
            token=access_token,
            roles=self._parse_roles(token_contents),
        )

    @staticmethod
    def _parse_roles(token_contents: TokenContents) -> list[Role]:
        formatted_roles = []
        for role in token_contents.roles:
            if role in Role._value2member_map_:
                formatted_roles.append(Role(role))
        return formatted_roles


class RBACSecurity:
    @staticmethod
    def verify(
        additional_roles: SecurityScopes,
        user: Annotated[User, Depends(OAuth())],
        required_role: Role = settings.AUTH_REQUIRED_ROLE,
    ) -> User:
        missing_roles = []
        for role in [required_role] + additional_roles.scopes:
            if role not in user.roles:
                missing_roles.append(role)

        if len(missing_roles) > 0:
            raise InsufficientPermissionsError(missing_roles)

        return user
