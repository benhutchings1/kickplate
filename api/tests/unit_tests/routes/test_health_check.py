import pytest
from fastapi.testclient import TestClient


def test_should_return_healthy_response(test_client: TestClient):
    response = test_client.get("/")

    assert response.json() == {"status": "ok"}
    assert response.status_code == 200
