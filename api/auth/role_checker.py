from typing import Any, List, Annotated, Optional
from fastapi import Header
from .token_validator import TokenValidator
from .dtos import TokenContents
from .errors import InsufficientPermissionsError


class RoleChecker():
    def __init__(self, required_roles: List[str], token_validator: Optional[TokenValidator] = None) -> None:
        self.required_roles = required_roles

        self.token_validator = token_validator
        if self.token_validator is None:
            self.token_validator = TokenValidator()

    def __call__(self, x_token: Annotated[str, Header()]) -> Any:
        token_contents: TokenContents = self.token_validator.verify_token(x_token)

        missing_roles = []
        for role in self.required_roles:
            if role not in token_contents.roles:
                missing_roles.append(role)

        if len(missing_roles) > 0:
            raise InsufficientPermissionsError(missing_roles)
