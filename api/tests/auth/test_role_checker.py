from unittest.mock import Mock
from auth.dtos import TokenContents
from auth.role_checker import RoleChecker
from auth.token_validator import TokenValidator
from auth.errors import InsufficientPermissionsError
import pytest


@pytest.fixture()
def token_contents() -> TokenContents:
    return TokenContents(email="fake@fake.com", roles=["role1", "role2"])


def test_role_checker(token_contents: TokenContents) -> None:
    mock_token_validator = Mock(spec=TokenValidator)
    mock_token_validator.verify_token.return_value = token_contents
    RoleChecker(required_roles=["role1"], token_validator=mock_token_validator)(
        x_token=None
    )


def test_role_checker_should_raise_error_on_missing_roles(
    token_contents: TokenContents,
) -> None:
    mock_token_validator = Mock(spec=TokenValidator)
    mock_token_validator.verify_token.return_value = token_contents

    required_roles = ["role2", "role3"]

    with pytest.raises(InsufficientPermissionsError) as exc:
        RoleChecker(
            required_roles=required_roles, token_validator=mock_token_validator
        )(x_token=None)
    assert exc.value.missing_roles == ["role3"]
