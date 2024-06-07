from com_utils.error_handling import CustomError, HttpCodes
from com_utils.logger import LoggingLevel, Loggers
import jwt
import json
import requests
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import base64
from config import ApiSettings


class TokenValidator:
    def verify_token(self, token: str) -> dict[str, str]:
        try:
            # Get public key
            pub_key = self.__get_rsa_key(token, ApiSettings.auth_open_id_config)
            # Verify JWT token using public key
            return jwt.decode(
                token,
                pub_key,
                verify=True,
                algorithms=["RS256"],
                audience=ApiSettings.auth_audience,
                issuer=ApiSettings.auth_issuer,
            )
        except jwt.exceptions.InvalidTokenError as ite:
            # Handle invalid token
            raise CustomError(
                error_code=HttpCodes.USER_UNAUTHORISED,
                logging_message=f"Error decoding key, message: {repr(ite)}",
                message="Invalid token",
                logging_level=LoggingLevel.INFO,
                logger=Loggers.SECURITY,
            )
        except jwt.exceptions.ExpiredSignatureError as ese:
            # Handle out of date token
            raise CustomError(
                error_code=HttpCodes.USER_UNAUTHORISED,
                logging_message=f"Token out of date, message: {repr(ese)}",
                message="Token out of date",
                logging_level=LoggingLevel.INFO,
                logger=Loggers.SECURITY,
            )
        except Exception as ge:
            # General error handler
            raise CustomError(
                error_code=HttpCodes.USER_UNAUTHORISED,
                logging_message=f"General token invalid error; type: {type(ge)}; message: {repr(ge)}",
                message="Error validating token",
                logging_level=LoggingLevel.INFO,
                logger=Loggers.SECURITY,
            )

    def __get_rsa_key(self, token: str, open_id_config_url: str) -> RSAPublicNumbers:
        """Converts public key from token header into RSA key"""
        # Get headers of JWT token
        unverified_headers = self.__get_jwt_headers(token)
        # Get key ID from headers
        kid = unverified_headers["kid"]
        # Get Entra ID OpenID public config
        pub_config = self.__request_url_contents(open_id_config_url)
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
            raise CustomError(
                error_code=HttpCodes.USER_UNAUTHORISED,
                message="Invalid bearer token",
                logging_message=f"{kid} not found in keyset",
                logging_level=LoggingLevel.INFO,
                logger=Loggers.SECURITY,
            )

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
