from unittest.mock import Mock, patch

import pytest
from faker import Faker
from fastapi.security import SecurityScopes

from auth.errors import InsufficientPermissionsError
from models.auth import Role, TokenContents, User
from auth.security import OAuth, RBACSecurity, rbac_security

fake = Faker()


def test_role_checker() -> None:
    user = User(
        email=fake.email(),
        roles=[Role.KICKPLATE_USER],
        token="",
    )
    required_scopes = SecurityScopes(scopes=[Role.KICKPLATE_USER])
    required_role = Role.KICKPLATE_USER
    security = rbac_security()

    returned_user = security(required_scopes, user, required_role)
    assert returned_user == user


def test_should_raise_error_for_no_roles():
    user = User(
        email=fake.email(),
        roles=[],
        token="",
    )
    required_role = Role.KICKPLATE_USER
    missing_role = Role.KICKPLATE_ADMIN
    required_scopes = SecurityScopes(scopes=[missing_role])

    with pytest.raises(InsufficientPermissionsError) as exc:
        RBACSecurity()(required_scopes, user, required_role)

    assert exc.value.missing_roles == [required_role, missing_role]


def test_should_raise_error_if_missing_role():
    user = User(
        email=fake.email(),
        roles=[Role.KICKPLATE_USER],
        token="",
    )
    required_role = Role.KICKPLATE_USER
    missing_role = Role.KICKPLATE_ADMIN
    required_scopes = SecurityScopes(scopes=[missing_role])
    security = RBACSecurity()

    with pytest.raises(InsufficientPermissionsError) as exc:
        security(required_scopes, user, required_role)

    assert exc.value.missing_roles == [missing_role]


def test_oauth():
    mock_token = "thisisanaccesstoken"

    user_roles = [Role.KICKPLATE_USER]

    mock_token_contents = TokenContents(
        email=fake.email(),
        roles=[a.value for a in user_roles],
    )

    expected_user = User(
        email=mock_token_contents.email,
        token=mock_token,
        roles=user_roles,
    )

    oauth = OAuth()

    class MockValidator:
        def decode_verify_token(self, access_token: str):
            assert access_token == mock_token
            return mock_token_contents

    returned_user = oauth(mock_token, MockValidator())
    assert returned_user == expected_user
