import base64
import json

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

from .errors import TokenExpiredError, TokenDecodingError

import binascii
from .dtos import TokenContents
from settings import settings


class TokenValidator:
    def __init__(self) -> None:
        self.jwks_url = settings.AUTH_JWKS_URL
        self.audience = settings.AUTH_AUDIENCE
        self.issuer = settings.AUTH_ISSUER

    def verify_token(
        self,
        token: str,
        *,
        verify_expiry=True,
    ) -> TokenContents:
        try:
            # Get public key
            __pub_key = self.__get_rsa_key(token, self.jwks_url)
            # Verify JWT token using public key
            return jwt.decode(
                token,
                __pub_key,
                verify=True,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={"verify_exp": verify_expiry},
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpiredError()
        except (jwt.exceptions.InvalidTokenError, binascii.Error, KeyError):
            raise TokenDecodingError()

    def __get_rsa_key(self, token: str, jwks_url: str) -> RSAPublicNumbers:
        """Converts public key from token header into RSA key"""
        # Get headers of JWT token
        unverified_headers = self.__get_jwt_headers(token)
        # Get key ID from headers
        kid = unverified_headers["kid"]
        # Get JWKS
        pub_config = self.__request_url_contents(jwks_url)
        # Get JWKS
        jwks_uri = pub_config["jwks_uri"]
        jwks = self.__request_url_contents(jwks_uri)

        # Find matching KID in public keyset
        jwk_key = None
        for keyset in jwks["keys"]:
            if kid == keyset["kid"]:
                jwk_key = keyset

        # No matching KID found, return invalid key
        if jwk_key is None:
            raise KeyError()

        # Format public JWK as RSA PEM
        return self.__rsa_pem_from_jwk(
            {
                "kty": jwk_key["kty"],
                "kid": jwk_key["kid"],
                "use": jwk_key["use"],
                "n": jwk_key["n"],
                "e": jwk_key["e"],
            }
        )

    @staticmethod
    def __get_jwt_headers(jwt_token: str) -> dict[str, str]:
        """Decode unverified JWT header"""
        header = jwt_token.split(".")[0]
        return json.loads(base64.b64decode(header).decode("utf-8"))

    @staticmethod
    def __request_url_contents(url) -> dict[str, str]:
        """Gets JSON response from given URL (Cached)"""
        return json.loads(requests.get(url).content)

    @staticmethod
    def __ensure_bytes(key) -> str:
        """Ensure UTF-8 encoding of string"""
        if isinstance(key, str):
            key = key.encode("utf-8")
        return key

    def __rsa_pem_from_jwk(self, jwk) -> RSAPublicNumbers:
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
