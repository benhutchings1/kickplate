class AuthenticationErrors(Exception):
    """Parent class for all API auth errors"""

    pass


class TokenExpiredError(AuthenticationErrors):
    """Token provided was expired error"""

    pass


class InsufficientPermissionsError(AuthenticationErrors):
    """User doesn't have required permissions to access route"""

    def __init__(self, missing_roles: list[str]) -> None:
        err_msg = f"Insufficient permissions to perform this action, missing roles: {missing_roles}"
        self.missing_roles = missing_roles
        super().__init__(err_msg)


class TokenDecodingError(AuthenticationErrors):
    """Invalid token structure, couldnt decode"""

    def __init__(self) -> None:
        super().__init__(f"Unable to decode provided token")


class InvalidTokenError(AuthenticationErrors):
    """Error if invalid token is provided"""

    def __init__(self) -> None:
        super().__init__(f"Invalid token provided")


class NoAuthorizationHeaderInRequestError(AuthenticationErrors):
    """Error if no authorization is in the request headers"""

    def __init__(self):
        super().__init__("No 'Authorization' header in request")


class HeaderDecodeError(AuthenticationErrors):
    """Error if header couldn't be decoded"""

    def __init__(self):
        super().__init__(
            "Could not decode authorization header, should be in format 'Bearer <token>'"
        )
