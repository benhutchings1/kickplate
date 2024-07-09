from auth.validator import TokenValidator
import pytest
import json
import logging
import requests_mock
from typing import cast
from com_utils.error_handling import CustomError
from com_utils.http import HttpCodes


@pytest.fixture
def flow_params():
    return {
        "authorizationUrl": "auth_url",
        "tokenUrl": "token_url",
        "scheme_name": "test_scheme_name",
        "scopes": {scope: scope for scope in ["scope1", "scope2"]},
        "description": "test description",
    }


@pytest.fixture
def data_path() -> str:
    return "tests/unit_tests/auth/data"


@pytest.fixture
def valid_token(data_path: str) -> str:
    with open(data_path + "/token.json") as fs:
        return json.load(fs)


@pytest.fixture
def valid_jwks(data_path: str) -> dict[str, str]:
    with open(data_path + "/jwks.json") as fs:
        return json.load(fs)


@pytest.fixture
def valid_oidc_config(data_path: str) -> dict[str, str]:
    with open(data_path + "/oidc_config.json") as fs:
        return json.load(fs)


def test_should_allow_valid_expired_token(
    valid_token: str, valid_jwks: dict[str, str], valid_oidc_config: dict[str, str]
):
    jwks_url = "https://jwks.com"
    oidc_config_url = "https://oidc.com"
    valid_oidc_config["jwks_uri"] = jwks_url

    token = valid_token["token"]
    audience = valid_token["audience"]
    issuer = valid_token["issuer"]

    # Replace oidc_config url
    with requests_mock.Mocker() as m:
        m = cast(requests_mock.Mocker, m)
        m.get(jwks_url, json=valid_jwks)
        m.get(oidc_config_url, json=valid_oidc_config)

        TokenValidator().verify_token(
            token=token,
            jwks_url=oidc_config_url,
            audience=audience,
            issuer=issuer,
            verify_expiry=False,
        )


def test_should_raise_expiry_error(
    valid_token: str, valid_jwks: dict[str, str], valid_oidc_config: dict[str, str]
):
    jwks_url = "https://jwks.com"
    oidc_config_url = "https://oidc.com"
    valid_oidc_config["jwks_uri"] = jwks_url

    token = valid_token["token"]
    audience = valid_token["audience"]
    issuer = valid_token["issuer"]

    # Replace oidc_config url
    with requests_mock.Mocker() as m:
        m = cast(requests_mock.Mocker, m)
        m.get(jwks_url, json=valid_jwks)
        m.get(oidc_config_url, json=valid_oidc_config)

        with pytest.raises(CustomError) as exc:
            TokenValidator().verify_token(
                token=token,
                jwks_url=oidc_config_url,
                audience=audience,
                issuer=issuer,
                verify_expiry=True,
            )
        assert exc.value.error_code == HttpCodes.USER_UNAUTHORISED
        assert exc.value.message == "Token out of date"


def test_should_raise_error_on_invalid_token(
    valid_token: str, valid_jwks: dict[str, str], valid_oidc_config: dict[str, str]
):
    jwks_url = "https://jwks.com"
    oidc_config_url = "https://oidc.com"
    valid_oidc_config["jwks_uri"] = jwks_url

    token = "1fdwf.srfgfbdsg.dsafg=="
    audience = valid_token["audience"]
    issuer = valid_token["issuer"]

    # Replace oidc_config url
    with requests_mock.Mocker() as m:
        m = cast(requests_mock.Mocker, m)
        m.get(jwks_url, json=valid_jwks)
        m.get(oidc_config_url, json=valid_oidc_config)

        with pytest.raises(CustomError) as exc:
            TokenValidator().verify_token(
                token=token,
                jwks_url=oidc_config_url,
                audience=audience,
                issuer=issuer,
                verify_expiry=True,
            )
        assert exc.value.error_code == HttpCodes.USER_UNAUTHORISED
        assert exc.value.message == "Invalid token"


def test_should_raise_error_on_missing_kid(
    valid_token: str, valid_jwks: dict[str, str], valid_oidc_config: dict[str, str]
):
    jwks_url = "https://jwks.com"
    oidc_config_url = "https://oidc.com"
    valid_oidc_config["jwks_uri"] = jwks_url

    token = valid_token["token"]
    audience = valid_token["audience"]
    issuer = valid_token["issuer"]

    # Remove keys
    valid_jwks["keys"] = []

    # Replace oidc_config url
    with requests_mock.Mocker() as m:
        m = cast(requests_mock.Mocker, m)
        m.get(jwks_url, json=valid_jwks)
        m.get(oidc_config_url, json=valid_oidc_config)

        with pytest.raises(CustomError) as exc:
            TokenValidator().verify_token(
                token=token,
                jwks_url=oidc_config_url,
                audience=audience,
                issuer=issuer,
                verify_expiry=True,
            )
        assert exc.value.error_code == HttpCodes.USER_UNAUTHORISED
        assert exc.value.logging_message == "kid not found in keyset"
