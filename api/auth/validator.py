import base64
import binascii
import json
from typing import Any, cast

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

from models.auth import TokenContents
from settings import settings

from .errors import InvalidTokenError, TokenDecodingError, TokenExpiredError


class TokenValidator:
    def __init__(self, audience: str, issuer: str, jwks_url: str) -> None:
        self.jwks = self._fetch_jwks(jwks_url)
        self._audience = audience
        self._issuer = issuer

    def _fetch_jwks(self, jwks_url: str) -> dict[str, Any]:
        pub_config = self.__request_url_contents(jwks_url)
        jwks_uri = pub_config["jwks_uri"]
        return self.__request_url_contents(jwks_uri)

    def decode_verify_token(
        self,
        token: str,
        *,
        verify_expiry=True,
    ) -> TokenContents:
        try:
            # Get public key
            __pub_key = self.__get_rsa_key(token)
            # Verify JWT token using public key
            token_contents = jwt.decode(
                token,
                __pub_key,
                verify=True,
                algorithms=["RS256"],
                audience=self._audience,
                issuer=self._issuer,
                options={"verify_exp": verify_expiry},
            )
            return TokenContents.model_validate(token_contents)

        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpiredError()
        except (jwt.exceptions.InvalidTokenError, binascii.Error, KeyError):
            raise TokenDecodingError()

    def __get_rsa_key(self, token: str) -> bytes:
        """Converts public key from token header into RSA key"""
        unverified_headers = self.__get_jwt_headers(token)
        kid = unverified_headers["kid"]
        jwk_key = None
        for keyset in self.jwks["keys"]:
            if kid == keyset["kid"]:
                jwk_key = keyset

        # No matching KID found, return invalid key
        if jwk_key is None:
            raise InvalidTokenError()

        # Format public JWK as RSA PEM
        return self.__rsa_pem_from_jwk(jwk_key)

    @staticmethod
    def __get_jwt_headers(jwt_token: str) -> dict[str, str]:
        """Decode unverified JWT header"""
        header = jwt_token.split(".")[0]
        return cast(
            dict[str, str], json.loads(base64.b64decode(header).decode("utf-8"))
        )

    @staticmethod
    def __request_url_contents(url) -> dict[str, str]:
        """Gets JSON response from given URL (Cached)"""
        return cast(dict[str, str], requests.get(url).json())

    @staticmethod
    def __ensure_bytes(key: str | bytes) -> bytes:
        """Ensure UTF-8 encoding of string"""
        if isinstance(key, str):
            key = key.encode("utf-8")
        return key

    def __rsa_pem_from_jwk(self, jwk: dict[str, Any]) -> bytes:
        """Format JWK as RSA Pub Number, PEM format"""
        return (
            RSAPublicNumbers(
                n=self.__decode_value(jwk["n"]), e=self.__decode_value(jwk["e"])
            )
            .public_key(default_backend())
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    def __decode_value(self, val) -> int:
        """Decode from Base64 to int"""
        decoded = base64.urlsafe_b64decode(self.__ensure_bytes(val) + b"==")
        return int.from_bytes(decoded, "big")


_token_validator: TokenValidator | None = None


def get_token_validator() -> TokenValidator:
    return cast(TokenValidator, _token_validator)


def initialise_token_validator() -> None:
    global _token_validator
    _token_validator = TokenValidator(
        settings.AUTH_AUDIENCE, settings.AUTH_ISSUER, settings.AUTH_OIDC_CONFIG_URL
    )
