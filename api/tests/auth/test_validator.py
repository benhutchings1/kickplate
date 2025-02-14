import json
from typing import Any, cast

import pytest
import requests_mock

from auth.errors import TokenDecodingError, TokenExpiredError
from auth.validator import TokenValidator


def test_should_allow_valid_token(
    valid_token: dict[str, str],
    valid_jwks: dict[str, str],
    valid_oidc_config: dict[str, str],
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

        token_validator = TokenValidator(audience, issuer, oidc_config_url)

    token_contents = token_validator.decode_verify_token(
        token,
        verify_expiry=False,
    )


def test_should_raise_expiry_error(
    valid_token: dict[str, str],
    valid_jwks: dict[str, str],
    valid_oidc_config: dict[str, str],
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

        token_validator = TokenValidator(audience, issuer, oidc_config_url)

    with pytest.raises(TokenExpiredError) as exc:
        token_contents = token_validator.decode_verify_token(
            token,
        )


def test_should_raise_error_on_invalid_token(
    valid_token: dict[str, str],
    valid_jwks: dict[str, str],
    valid_oidc_config: dict[str, str],
):
    jwks_url = "https://jwks.com"
    oidc_config_url = "https://oidc.com"
    valid_oidc_config["jwks_uri"] = jwks_url

    token = "1fdwf.srfgfbdsg.dsafg=="
    audience = valid_token["audience"]
    issuer = valid_token["issuer"]

    with requests_mock.Mocker() as m:
        m = cast(requests_mock.Mocker, m)
        m.get(jwks_url, json=valid_jwks)
        m.get(oidc_config_url, json=valid_oidc_config)

        token_validator = TokenValidator(audience, issuer, oidc_config_url)

    with pytest.raises(TokenDecodingError) as exc:
        token_contents = token_validator.decode_verify_token(
            token,
        )


def test_should_raise_error_on_missing_kid(
    valid_token: dict[str, str],
    valid_jwks: dict[str, Any],
    valid_oidc_config: dict[str, Any],
):
    jwks_url = "https://jwks.com"
    oidc_config_url = "https://oidc.com"
    valid_oidc_config["jwks_uri"] = jwks_url
    valid_jwks["keys"] = []

    token = "1fdwf.srfgfbdsg.dsafg=="
    audience = valid_token["audience"]
    issuer = valid_token["issuer"]

    with requests_mock.Mocker() as m:
        m = cast(requests_mock.Mocker, m)
        m.get(jwks_url, json=valid_jwks)
        m.get(oidc_config_url, json=valid_oidc_config)

        token_validator = TokenValidator(audience, issuer, oidc_config_url)

    with pytest.raises(TokenDecodingError) as exc:
        token_contents = token_validator.decode_verify_token(
            token,
        )
