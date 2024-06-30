from typing import Union
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from requests import Request

from app import app
from auth.auth_flow import oauth_scheme
from external.kubenetes import KubernetesConn

GRAPH_TYPING = dict[str, Union[str, dict[str, Union[str, dict]]]]


@pytest.fixture
def test_client_auth() -> TestClient:
    return TestClient(app)


class MockAuth:
    async def __call__(request: Request):
        return request


@pytest.fixture
def test_client() -> TestClient:
    app.dependency_overrides[oauth_scheme] = MockAuth
    return TestClient(app)


@pytest.fixture
def k8s_client() -> KubernetesConn:
    client = KubernetesConn()
    client.create_resource = MagicMock()
    client.get_resource = MagicMock()
    return client


def mock_k8s_factory(get_resource_return: GRAPH_TYPING = None) -> object:
    class MockK8s:
        def create_resource(self, group, version, namespace, plural, body):
            return

        def get_resource(self, name, group, version, namespace, plural):
            return get_resource_return

    return MockK8s


class MockHTTPResponse:
    def __init__(self, status=None, reason=None, data=None):
        self.status = status
        self.reason = reason
        self.data = data

    def getheaders(self):
        return {"fakekey": "fakeval"}
