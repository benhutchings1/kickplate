# from auth.auth_flow import OAuthCodeFlow
# import pytest
# from typing import List, Union
# from requests import Request
# import logging
# from unittest.mock import MagicMock


# @pytest.fixture
# def flow_params():
#     return {
#         "authorizationUrl": "auth_url",
#         "tokenUrl": "token_url",
#         "scheme_name": "test_scheme_name",
#         "scopes": {scope: scope for scope in ["scope1", "scope2"]},
#         "description": "test description",
#     }


# @pytest.fixture
# def valid_flow(flow_params: dict[str, Union[str, List[str]]]):
#     return OAuthCodeFlow(**flow_params)


# @pytest.mark.asyncio
# async def test_should_allow_whitelisted_route_to_pass(
#     valid_flow: OAuthCodeFlow,
# ):
#     with MagicMock() as mm:
#         mock_request = mm
#         mm.scope = {"path": "/docs"}

#         await logging.warning(valid_flow(mock_request))
