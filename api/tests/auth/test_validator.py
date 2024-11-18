from auth.token_validator import TokenValidator
import pytest
import json
from typing import cast
import requests_mock
from auth.errors import TokenExpiredError, TokenDecodingError


@pytest.fixture
def data_path() -> str:
    return "tests/auth/data"


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

        with pytest.raises(TokenExpiredError) as exc:
            TokenValidator().verify_token(
                token=token,
                jwks_url=oidc_config_url,
                audience=audience,
                issuer=issuer,
                verify_expiry=True,
            )


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

        with pytest.raises(TokenDecodingError) as exc:
            TokenValidator().verify_token(
                token=token,
                jwks_url=oidc_config_url,
                audience=audience,
                issuer=issuer,
                verify_expiry=True,
            )
