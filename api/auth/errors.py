from typing import List


class APIAuthErrors(Exception):
    """Parent class for all API auth errors"""

    pass


class TokenExpiredError(APIAuthErrors):
    """Token provided was expired error"""

    pass


class InsufficientPermissionsError(APIAuthErrors):
    """User doesn't have required permissions to access route"""

    def __init__(self, missing_roles: List[str]) -> None:
        super().__init__(
            f"User does not have required permissions to perform this action. Required roles: {missing_roles}"
        )
        self.missing_roles = missing_roles


class TokenDecodingError(APIAuthErrors):
    """Invalid token structure, couldnt decode"""

    pass
