import json
from typing import Union, cast
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from kubernetes.client.exceptions import ApiException

from app import app
from com_utils.error_handling import CustomError
from api.external.cluster import K8Client
from routes.graph_status.graph_status import GraphStatus
from tests.unit_tests.conftest import MockHTTPResponse, mock_k8s_factory
from com_utils.http import HttpCodes


GRAPH_TYPING = dict[str, Union[str, dict[str, Union[str, dict]]]]


@pytest.fixture
def sample_execution_info() -> GRAPH_TYPING:
    return {
        "metadata": {
            "labels": {
                "workflows.argoproj.io/completed": "test_complete",
                "workflows.argoproj.io/phase": "test_phase",
            },
            "name": "test_workflow",
            "creationTimestamp": "12/12/12",
        },
        "status": {
            "nodes": {
                "step1": {
                    "displayName": "test_display_name",
                    "phase": "test_phase",
                    "startedAt": "test_start_time",
                    "finishedAt": "test_finished_time",
                    "message": "this is a test message",
                },
                "step2": {
                    "displayName": "test_display_name2",
                    "phase": "test_phase2",
                    "startedAt": "test_start_time2",
                    "finishedAt": "test_finished_time2",
                    "message": "this is a test message2",
                },
                "test_workflow": {},
            }
        },
    }


@pytest.fixture
def sample_formatted_status(sample_execution_info: GRAPH_TYPING) -> GRAPH_TYPING:
    step1: dict = sample_execution_info["status"]["nodes"]["step1"]
    step2: dict = sample_execution_info["status"]["nodes"]["step2"]

    return {
        "graphname": sample_execution_info["metadata"]["name"],
        "completed_time": sample_execution_info["metadata"]["labels"][
            "workflows.argoproj.io/completed"
        ],
        "phase": sample_execution_info["metadata"]["labels"][
            "workflows.argoproj.io/phase"
        ],
        "creation_time": sample_execution_info["metadata"]["creationTimestamp"],
        "steps_status": [
            {
                "name": step1["displayName"],
                "state": step1["phase"],
                "start_time": step1["startedAt"],
                "finish_time": step1.get("finishedAt", None),
                "error_message": step1.get("message", None),
            },
            {
                "name": step2["displayName"],
                "state": step2["phase"],
                "start_time": step2["startedAt"],
                "finish_time": step2.get("finishedAt", None),
                "error_message": step2.get("message", None),
            },
        ],
    }


@pytest.fixture
def execution_id() -> str:
    return "test_exec_id"


def test_route_should_return_id_of_execution(
    test_client: TestClient,
    execution_id: str,
    sample_execution_info: GRAPH_TYPING,
    sample_formatted_status: GRAPH_TYPING,
):
    app.dependency_overrides[K8Client] = mock_k8s_factory(sample_execution_info)
    resp = test_client.get(f"/graph/{execution_id}")
    assert json.loads(resp.content) == sample_formatted_status


def test_should_return_execution_info(
    k8s_client: K8Client,
    execution_id: str,
    sample_formatted_status: GRAPH_TYPING,
    sample_execution_info: GRAPH_TYPING,
):
    k8s_client.get_resource = cast(MagicMock, k8s_client.get_resource)
    k8s_client.get_resource.return_value = sample_execution_info

    exec_desc = GraphStatus(k8s_client).get_graph_status(execution_id)

    assert exec_desc == sample_formatted_status


def test_should_raise_error_on_missing_graph(
    k8s_client: K8Client,
    execution_id: str,
):
    k8s_client.get_resource = cast(MagicMock, k8s_client.get_resource)
    k8s_client.get_resource.side_effect = ApiException(
        http_resp=MockHTTPResponse("404", "test", b'{"code": "404"}')
    )

    with pytest.raises(CustomError) as e:
        GraphStatus(k8s_client).get_graph_status(execution_id)

    assert e.value.error_code == HttpCodes.NOT_FOUND
