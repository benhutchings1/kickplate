from typing import Annotated, cast

from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes

from settings import settings

from .errors import InsufficientPermissionsError
from .models import Roles, Scopes, TokenContents, User
from .validator import TokenValidator, get_token_validator

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.AUTH_AUTH_URL,
    tokenUrl=settings.AUTH_TOKEN_URL,
    scopes={scope.value: "" for scope in Scopes._member_map_.values()},
)


class OAuth:
    def __call__(
        self,
        access_token: Annotated[str, Depends(oauth2_scheme)],
        token_validator: Annotated[TokenValidator, Depends(get_token_validator)],
    ) -> User:
        token_contents: TokenContents = token_validator(access_token)
        return User(
            email=token_contents.email,
            token=access_token,
            scopes=self._parse_scopes(token_contents),
            roles=self._parse_roles(token_contents),
        )

    @staticmethod
    def _parse_roles(token_contents: TokenContents) -> list[Roles]:
        formatted_roles = []
        for role in token_contents.roles:
            if role in Roles._member_map_:
                formatted_roles.append(Roles[role])
        return formatted_roles

    @staticmethod
    def _parse_scopes(token_contents: TokenContents) -> list[Scopes]:
        formatted_scopes = []
        for scope in token_contents.scopes:
            if scope in Scopes._member_map_:
                formatted_scopes.append(Scopes[scope])
        return formatted_scopes


class RBACSecurity:
    def __init__(
        self, required_role: list[Roles] = settings.AUTH_REQUIRED_ROLES
    ) -> None:
        self._required_roles = required_role

    def __call__(
        self, required_scopes: SecurityScopes, user: Annotated[User, Depends(OAuth())]
    ) -> User:
        self._verify_roles_and_scopes(
            user.roles,
            user.scopes,
            cast(list[Scopes], required_scopes.scopes),
        )

        return user

    def _verify_roles_and_scopes(
        self,
        user_roles: list[Roles],
        user_scopes: list[Scopes],
        required_scopes: list[Scopes],
    ) -> None:
        missing_roles = []
        for role in self._required_roles:
            if role not in user_roles:
                missing_roles.append(role)

        missing_scopes = []
        for scope in required_scopes:
            if scope not in user_scopes:
                missing_scopes.append(scope)

        if len(missing_roles) > 0 or len(missing_scopes) > 0:
            raise InsufficientPermissionsError(missing_roles, missing_scopes)
