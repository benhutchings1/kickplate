import pytest
from fastapi.testclient import TestClient
from routes.run_graph.run_exec_graph import RunGraph
from unittest.mock import MagicMock


def test_should_return_healthy_response(test_client: TestClient):
    exec_id = "test_exec_id"

    response = test_client.get(f"/graph/{exec_id}")
    assert response.status_code == 200
