from auth.auth_flow import OAuthCodeFlow
import pytest
from typing import List, Union
from unittest.mock import MagicMock
from config import ApiSettings
from com_utils.error_handling import CustomError
from com_utils.http import HttpCodes
from fastapi.testclient import TestClient
import json
import jwt
from mock import patch
from app import app
from external.kubenetes import K8_Client
from tests.unit_tests.conftest import MockHTTPResponse, mock_k8s_factory



@pytest.fixture
def data_path() -> str:
    return "tests/unit_tests/auth/data"


@pytest.fixture
def valid_token(data_path: str) -> str:
    with open(data_path + "/token.json") as fs:
        return json.load(fs)["token"]


@pytest.fixture
def valid_token_contents(valid_token: str) -> dict[str, str]:
    return jwt.decode(valid_token, key=None, options={"verify_signature": False})


@pytest.fixture
def valid_flow(flow_params: dict[str, Union[str, List[str]]]):
    return OAuthCodeFlow(**flow_params)


@pytest.fixture
def flow_params():
    return {
        "authorizationUrl": "auth_url",
        "tokenUrl": "token_url",
        "scheme_name": "test_scheme_name",
        "scopes": {scope: scope for scope in ["scope1", "scope2"]},
        "description": "test description",
    }


@patch("config.ApiSettings.auth_enable", True)
def test_should_return_error_response_on_missing_token(
    test_client_auth: TestClient
):
    resp = test_client_auth.get("/graph/test_id")
    
    assert resp.status_code == 401
    assert json.loads(resp.text)["error"] == "Bearer token required"

    
@patch("config.ApiSettings.auth_enable", True)
@pytest.mark.asyncio
async def test_should_allow_whitelisted_route_to_pass(
    valid_flow: OAuthCodeFlow,
):
    with MagicMock() as mm:
        mock_request = mm
        mm.scope = {"path": "/docs"}
        await valid_flow(mock_request)


@patch("config.ApiSettings.auth_enable", True)
@pytest.mark.asyncio
async def test_should_raise_error_on_missing_bearer_token(
    valid_flow: OAuthCodeFlow,
):
    with MagicMock() as mm:
        mock_request = mm
        mm.scope = {"path": "/somepath"}
        ApiSettings.auth_enable = True

        with pytest.raises(CustomError) as exc:
            await valid_flow(mock_request)

        assert exc.value.error_code == HttpCodes.USER_UNAUTHORISED
        assert exc.value.message == "Bearer token required"


@patch("config.ApiSettings.auth_enable", True)
@pytest.mark.asyncio
async def test_should_allow_valid_token(
    valid_flow: OAuthCodeFlow, valid_token: str, valid_token_contents: dict[str, str]
):
    with MagicMock() as mm:
        mm.scope = {"path": "/somepath"}
        mm.headers = {"authorization": f"authorization {valid_token}"}
        mm.verify_token.return_value = valid_token_contents
        ApiSettings.auth_enable = True
        valid_flow.token_validator = mm

        group = "this-is-the-id"
        ApiSettings.auth_group_id = group
        valid_token_contents["groups"] = [group]

        await valid_flow(mm)


@patch("config.ApiSettings.auth_enable", True)
@patch("config.ApiSettings.auth_group_id", "this-is-the-id")
@pytest.mark.asyncio
async def test_should_raise_error_on_missing_group(
    valid_flow: OAuthCodeFlow, valid_token: str, valid_token_contents: dict[str, str]
):
    with MagicMock() as mm:
        mm.scope = {"path": "/somepath"}
        mm.headers = {"authorization": f"authorization {valid_token}"}
        mm.verify_token.return_value = valid_token_contents
        ApiSettings.auth_enable = True
        valid_flow.token_validator = mm
        ApiSettings.auth_group_id = "this-is-the-id"

        with pytest.raises(CustomError) as exc:
            await valid_flow(mm)

        exc.value.error_code == HttpCodes.USER_UNAUTHORISED
        exc.value.message == "User not member of security group"
