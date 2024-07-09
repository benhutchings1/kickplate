import json
from typing import Union, cast
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from kubernetes.client.exceptions import ApiException

from app import app
from com_utils.backup_exception import BackupException
from com_utils.error_handling import CustomError
from external.kubenetes import K8_Client
from routes.create_graph.create_exec_graph import CreateExecGraph
from tests.unit_tests.conftest import MockHTTPResponse, mock_k8s_factory

GRAPH_TYPING = dict[str, Union[str, dict[str, Union[str, dict]]]]


@pytest.fixture
def sample_graph_def() -> GRAPH_TYPING:
    return {
        "graphname": "test_graph",
        "steps": [
            {
                "stepname": "step1",
                "image": "testimage",
                "env": {"test": "env"},
                "args": ["testarg"],
                "command": ["testcmd"],
            },
            {
                "stepname": "step2",
                "image": "testimage2",
                "dependencies": ["step1"],
            },
        ],
    }


@pytest.fixture
def sample_formatted_graph_def(sample_graph_def: GRAPH_TYPING) -> GRAPH_TYPING:
    # Fill missing default values
    default_params = {
        "env": {},
        "args": [],
        "command": [],
        "dependencies": [],
        "replicas": 1,
    }
    for step in sample_graph_def["steps"]:
        for param in default_params:
            if param not in step:
                step[param] = default_params[param]

    return {
        "group": "test.deploymentengine.com",
        "version": "v1",
        "plural": "execgraphs",
        "namespace": "argo",
        "body": {
            "metadata": {"name": sample_graph_def["graphname"]},
            "apiVersion": "v1",
            "kind": "ExecutionGraph",
            "spec": {"steps": sample_graph_def["steps"]},
        },
    }


def test_route_should_return_graph_name_on_correct_graph_definition(
    test_client: TestClient, sample_graph_def: GRAPH_TYPING
):
    app.dependency_overrides[K8_Client] = mock_k8s_factory(None)
    resp = test_client.post("/graph/create_graph", json=sample_graph_def)
    assert json.loads(resp.content)["graphname"] == sample_graph_def["graphname"]


def test_should_send_correct_graph_definition_request(
    k8s_client: K8_Client,
    sample_graph_def: GRAPH_TYPING,
    sample_formatted_graph_def: GRAPH_TYPING,
):
    graph_name = CreateExecGraph(k8s_client).submit_graph(sample_graph_def)
    k8s_client.create_resource = cast(MagicMock, k8s_client.create_resource)

    # Parse step output to json
    step_out = k8s_client.create_resource.call_args[1]["body"]["spec"].pop("steps")
    sample_steps = sample_formatted_graph_def["body"]["spec"].pop("steps")

    for i in range(len(step_out)):
        step_out[i] = json.loads(step_out[i])

    # Remove ordering by mapping steps to stepname
    sample_steps_dict = {}
    step_out_dict = {}

    for i in range(len(sample_steps)):
        sample_steps_dict[sample_steps[i]["stepname"]] = sample_steps[i]
        step_out_dict[step_out[i]["stepname"]] = step_out[i]

    assert step_out_dict == sample_steps_dict

    k8s_client.create_resource.assert_called_once()
    assert k8s_client.create_resource.call_args[1] == sample_formatted_graph_def
    assert graph_name == sample_graph_def["graphname"]


def test_should_raise_custom_error_on_failed_k8s_conn(sample_graph_def: GRAPH_TYPING):
    with pytest.raises(BackupException):
        CreateExecGraph(K8_Client()).submit_graph(sample_graph_def)


def test_should_raise_error_on_invalid_graph_name(
    k8s_client: K8_Client, sample_graph_def: GRAPH_TYPING
):
    sample_graph_def["graphname"] = "@?%*ndsiuhndusajiodjsoSABDIA"

    with pytest.raises(CustomError):
        CreateExecGraph(k8s_client).submit_graph(sample_graph_def)


def test_should_raise_error_on_duplicate_graph_name(
    k8s_client: K8_Client,
    sample_graph_def: GRAPH_TYPING,
):
    k8s_client.create_resource = cast(MagicMock, k8s_client.create_resource)
    k8s_client.create_resource.side_effect = ApiException(
        http_resp=MockHTTPResponse(409, "test", b'{"code": "409"}')
    )

    with pytest.raises(CustomError) as exc:
        CreateExecGraph(k8s_client).submit_graph(sample_graph_def)


def test_should_raise_error_on_missing_graphname(k8s_client: K8_Client):
    bad_graph_def = {"thisis": "bad"}

    with pytest.raises(CustomError) as exc:
        CreateExecGraph(k8s_client).submit_graph(bad_graph_def)


def test_should_raise_error_on_missing_steps(k8s_client: K8_Client):
    bad_graph_def = {"graphname": "bad"}

    with pytest.raises(CustomError) as exc:
        CreateExecGraph(k8s_client).submit_graph(bad_graph_def)


def test_should_raise_error_on_bad_steps_definition_not_list(
    k8s_client: K8_Client,
):
    bad_graph_def = {"graphname": "bad", "steps": {"thing": "notgood"}}

    with pytest.raises(CustomError) as exc:
        CreateExecGraph(k8s_client).submit_graph(bad_graph_def)


def test_should_raise_error_on_bad_steps_definition_not_model_valid(
    k8s_client: K8_Client,
):
    bad_graph_def = {"graphname": "bad", "steps": [{"this": "bad"}]}

    with pytest.raises(CustomError) as exc:
        CreateExecGraph(k8s_client).submit_graph(bad_graph_def)
