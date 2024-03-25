from src.config import config
from src.error_handling import CustomError, HttpCodes
from fastapi import Request
import jwt
import json
import requests
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import base64

# Routes to not perform auth on
WHITELIST_ROUTES = [
    "/",            # Health check
    "/docs",        # Swagger docs
    "/openapi.json" # Swagger docs requirements
]


async def check_auth(request: Request, call_next) -> None:
    '''Check for valid bearer token on non-whitelisted routes'''
    # Check for whitelisted routes request
    if request.scope['path'] in WHITELIST_ROUTES:
        return await call_next(request)
    
    # Check headers for bearer token authorisation 
    if not "token" in request.headers:
        raise CustomError(
            error_code=HttpCodes.USER_UNAUTHORISED,
            message="Bearer token required",
            logging_message=f"IP: {request.client.host} tried to access \
                {request.scope['path']} without a token")
    
    # Verify token
    token_contents = verify_token(str(request.headers["token"]))

    # Check group membership
    if not config.get("auth", "group_id") in token_contents["groups"]:
        raise CustomError(
            error_code=HttpCodes.USER_UNAUTHORISED,
            message="User not member of security group",
            logging_message=f"IP: {request.client.host} tried to access \
                {request.scope['path']} but isn't a member"            
        )
        
    return await call_next(request)


def verify_token(token:str) -> dict[str, str]:
    # Get config options
    open_id_config_url = config.get("auth", "open_id_config_url")
    audience = config.get("auth", "audience")
    issuer = config.get("auth", "issuer_url")
    
    try:
        # Get public key
        pub_key = __get_rsa_key(token, open_id_config_url)
        # Verify JWT token using public key
        return jwt.decode(
            token,
            pub_key,
            verify=True,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer
        )
    except jwt.exceptions.InvalidTokenError as ite:
        # Handle invalid token
        raise CustomError(
            error_code=HttpCodes.USER_UNAUTHORISED,
            logging_message=f"Error decoding key, message: {repr(ite)}",
            message="Invalid token"
        )
    except jwt.exceptions.ExpiredSignatureError as ese:
        # Handle out of date token
        raise CustomError(
            error_code=HttpCodes.USER_UNAUTHORISED,
            logging_message=f"Token out of date, message: {repr(ese)}",
            message="Token out of date"
        )
    except Exception as ge:
        # General error handler
        raise CustomError(
            error_code=HttpCodes.USER_UNAUTHORISED,
            logging_message=f"General token invalid error; type: {type(ge)}; message: {repr(ge)}",
            message="Error validating token"
        )
        
        
def __get_rsa_key(token:str, open_id_config_url:str) -> RSAPublicNumbers:
    '''Converts public key from token header into RSA key'''
    # Get headers of JWT token
    unverified_headers = __get_jwt_headers(token)
    # Get key ID from headers
    kid = unverified_headers["kid"]    
    # Get Entra ID OpenID public config
    pub_config = __request_url_contents(open_id_config_url)
    # Get JWKS
    jwks_uri = pub_config["jwks_uri"]
    jwks = __request_url_contents(jwks_uri)
    
    # Find matching KID in public keyset
    jwk_key = None
    for keyset in jwks["keys"]:
        if kid == keyset["kid"]:
            jwk_key = keyset
    
    # No matching KID found, return invalid key
    if jwk_key is None:
        raise CustomError(
            error_code=HttpCodes.USER_UNAUTHORISED,
            message=f"Invalid bearer token",
            logging_message=f"{kid} not found in keyset"
        )
    
    # Format public JWK as RSA PEM
    return __rsa_pem_from_jwk({
            "kty": jwk_key["kty"],
            "kid": jwk_key["kid"],
            "use": jwk_key["use"],
            "n": jwk_key["n"],
            "e": jwk_key["e"]
    })


def __get_jwt_headers(jwt_token:str) -> dict[str, str]:
    '''Decode unverified JWT header'''
    header = jwt_token.split(".")[0]
    return json.loads(base64.b64decode(header).decode("utf-8"))


def __request_url_contents(url) -> dict[str, str]:
    '''Gets JSON response from given URL (Cached)'''
    return json.loads(requests.get(url).content)


def __ensure_bytes(key) -> str:
    '''Ensure UTF-8 encoding of string'''
    if isinstance(key, str):
        key = key.encode('utf-8')
    return key


def __decode_value(val) -> int:
    '''Decode from Base64 to int'''
    decoded = base64.urlsafe_b64decode(__ensure_bytes(val) + b'==')
    return int.from_bytes(decoded, 'big')


def __rsa_pem_from_jwk(jwk) -> RSAPublicNumbers:
    '''Format JWK as RSA Pub Number, PEM format'''
    return RSAPublicNumbers(
        n=__decode_value(jwk['n']),
        e=__decode_value(jwk['e'])
    ).public_key(default_backend()).public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

