from unittest.mock import Mock, patch

import pytest
from faker import Faker
from fastapi.security import SecurityScopes

from auth.errors import InsufficientPermissionsError
from auth.models import Roles, Scopes, TokenContents, User
from auth.security import OAuth, RBACSecurity

fake = Faker()


def test_role_checker() -> None:
    user = User(
        email=fake.email(),
        scopes=[Scopes.EDAG_RUN, Scopes.EDAG_READ],
        roles=[Roles.KICKPLATE_USER],
        token="",
    )
    required_scopes = SecurityScopes(scopes=[Scopes.EDAG_RUN])
    required_role = [Roles.KICKPLATE_USER]
    security = RBACSecurity(required_role)

    returned_user = security(required_scopes, user)
    assert returned_user == user


def test_should_raise_error_if_missing_role():
    user = User(
        email=fake.email(),
        scopes=[Scopes.EDAG_RUN, Scopes.EDAG_READ],
        roles=[Roles.KICKPLATE_USER],
        token="",
    )
    required_scopes = SecurityScopes(scopes=[Scopes.EDAG_RUN])
    required_role = [Roles.KICKPLATE_ADMIN]
    security = RBACSecurity(required_role)

    with pytest.raises(InsufficientPermissionsError) as exc:
        security(required_scopes, user)

    assert exc.value.missing_roles == required_role
    assert exc.value.missing_scopes == []


def test_should_raise_error_if_missing_scope():
    user = User(
        email=fake.email(),
        scopes=[Scopes.EDAG_RUN, Scopes.EDAG_READ],
        roles=[Roles.KICKPLATE_USER],
        token="",
    )
    required_scopes = SecurityScopes(scopes=[Scopes.EDAG_DELETE])
    required_role = [Roles.KICKPLATE_USER]
    security = RBACSecurity(required_role)

    with pytest.raises(InsufficientPermissionsError) as exc:
        security(required_scopes, user)

    assert exc.value.missing_roles == []
    assert exc.value.missing_scopes == [Scopes.EDAG_DELETE]


def test_oauth():
    mock_token = "thisisanaccesstoken"

    roles = [Roles.KICKPLATE_USER]
    scopes = [Scopes.EDAG_DELETE, Scopes.EDAG_READ]

    mock_token_contents = TokenContents(
        email=fake.email(),
        roles=[a.value for a in roles],
        scopes=[a.value for a in scopes],
    )

    expected_user = User(
        email=mock_token_contents.email, token=mock_token, roles=roles, scopes=scopes
    )

    oauth = OAuth()

    class MockValidator:
        def __call__(self, access_token: str):
            assert access_token == mock_token
            return mock_token_contents

    returned_user = oauth(mock_token, MockValidator())
    assert returned_user == expected_user
