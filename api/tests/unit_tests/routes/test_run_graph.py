from typing import Union, cast
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from kubernetes.client.exceptions import ApiException
import json
from mock import patch

from app import app
from com_utils.error_handling import CustomError
from api.external.cluster import K8Client
from routes.run_graph.run_exec_graph import RunGraph
from tests.unit_tests.conftest import MockHTTPResponse, mock_k8s_factory
from com_utils.http import HttpCodes
from config import ApiSettings

GRAPH_TYPING = dict[str, Union[str, dict[str, Union[str, dict]]]]


@pytest.fixture
def sample_graph_definition() -> GRAPH_TYPING:
    return {
        "spec": {
            "steps": [
                {
                    "stepname": "step1",
                    "image": "image1",
                    "command": ["command", "1"],
                    "args": ["args", "1"],
                    "dependencies": [],
                },
                {
                    "stepname": "step2",
                    "image": "image2",
                    "command": ["command", "2"],
                    "args": ["args", "2"],
                    "dependencies": ["step1"],
                },
            ]
        }
    }

class MockApiSettings:   
    kube_graph_group="test_kube_graph_group"
    kube_graph_api_version="test_kube_graph_api_version"
    kube_graph_plural="test_kube_graph_plural"
    kube_namespace="test_kube_namespace"
    
    kube_workflow_api_version="test_kube_workflow_api_version"
    kube_workflow_kind="test_kube_workflow_kind"
    kube_workflow_group="test_kube_workflow_group"
    kube_workflow_plural="test_kube_workflow_plural"


@patch("config.ApiSettings", MockApiSettings)
@pytest.fixture
def sample_formatted_workflow(sample_graph_definition: GRAPH_TYPING) -> GRAPH_TYPING:
    template = []
    template_reference = []
    for step in sample_graph_definition["spec"]["steps"]:
        template.append(
            {
                "name": f"{step['stepname']}-template",
                "container": {
                    "image": f"{step['image']}",
                    "command": step["command"],
                    "args": step["args"],
                },
            }
        )
        template_reference.append(
            {
                "name": f"{step['stepname']}",
                "template": f"{step['stepname']}-template",
                "dependencies": step["dependencies"],
            }
        )
    template.append(
        {
            "name": "dag-workflow",
            "dag": {"tasks": template_reference},
        }
    )

    return {
        "apiVersion": ApiSettings.kube_workflow_api_version,
        "kind": ApiSettings.kube_workflow_kind,
        "metadata": {"name": ""},  # Replace with generated ID
        "spec": {"entrypoint": "dag-workflow", "templates": template},
    }


@pytest.fixture
def graph_name() -> str:
    return "test_graph_name"


def test_route_should_return_id_of_execution(
    test_client: TestClient, graph_name: str, sample_graph_definition: GRAPH_TYPING
):
    app.dependency_overrides[K8Client] = mock_k8s_factory(sample_graph_definition)
    resp = test_client.post(f"/graph/{graph_name}")
    assert json.loads(resp.content)["execution_id"][0:15] == graph_name


@patch("config.ApiSettings", MockApiSettings)
def test_should_send_correct_graph_definition_request(
    k8s_client: K8Client,
    graph_name: str,
    sample_graph_definition: GRAPH_TYPING,
    sample_formatted_workflow: GRAPH_TYPING,
):

    k8s_client.create_resource = cast(MagicMock, k8s_client.create_resource)

    k8s_client.get_resource = cast(MagicMock, k8s_client.get_resource)
    k8s_client.get_resource.return_value = sample_graph_definition

    exec_id = RunGraph(k8s_client=k8s_client).run_graph(graph_name)
    assert exec_id[0:15] == graph_name

    # assert on kubernetes paths
    k8s_client.get_resource.assert_called_once_with(
        name=graph_name,
        group=ApiSettings.kube_graph_group,
        version=ApiSettings.kube_graph_api_version,
        plural=ApiSettings.kube_graph_plural,
        namespace=ApiSettings.kube_namespace,
    )

    sample_formatted_workflow["metadata"]["name"] = exec_id
    k8s_client.create_resource.assert_called_once_with(
        group=ApiSettings.kube_workflow_group,
        version=ApiSettings.kube_workflow_api_version,
        plural=ApiSettings.kube_workflow_plural,
        namespace=ApiSettings.kube_namespace,
        body=sample_formatted_workflow,
    )


def test_should_raise_error_on_non_existent_graph(
    k8s_client: K8Client, graph_name: str
):
    k8s_client.get_resource = cast(MagicMock, k8s_client.get_resource)
    k8s_client.get_resource.side_effect = ApiException(
        http_resp=MockHTTPResponse("404", "test", b'{"code": "404"}')
    )

    with pytest.raises(CustomError) as e:
        RunGraph(k8s_client=k8s_client).run_graph(graph_name)

    assert e.value.error_code == HttpCodes.USER_ERROR


def test_should_raise_error_on_already_existing_workflow(
    k8s_client: K8Client, graph_name: str
):
    k8s_client.create_resource = cast(MagicMock, k8s_client.create_resource)
    k8s_client.create_resource.side_effect = ApiException(
        http_resp=MockHTTPResponse("409", "test", b'{"code": "409"}')
    )

    with pytest.raises(CustomError) as e:
        RunGraph(k8s_client=k8s_client).run_graph(graph_name)

    assert e.value.error_code == HttpCodes.USER_ERROR


def test_should_raise_error_on_non_existent_graph(
    k8s_client: K8Client, graph_name: str
):
    k8s_client.get_resource = cast(MagicMock, k8s_client.get_resource)
    k8s_client.get_resource.side_effect = ApiException(
        http_resp=MockHTTPResponse("404", "test", b'{"code": "404"}')
    )

    with pytest.raises(CustomError) as e:
        RunGraph(k8s_client=k8s_client).run_graph(graph_name)

    assert e.value.error_code == HttpCodes.USER_ERROR


def test_should_allow_unknown_errors_when_create_resource(
    k8s_client: K8Client, graph_name: str
):
    exc = ValueError("This is an error")
    k8s_client.create_resource = cast(MagicMock, k8s_client.create_resource)
    k8s_client.create_resource.side_effect = exc

    try:
        RunGraph(k8s_client=k8s_client).run_graph(graph_name)
    except Exception as e:
        assert not isinstance(e, CustomError)
        assert exc == e


def test_should_allow_unknown_errors_when_get_resource(
    k8s_client: K8Client, graph_name: str
):
    exc = ValueError("This is an error")
    k8s_client.get_resource = cast(MagicMock, k8s_client.get_resource)
    k8s_client.get_resource.side_effect = exc

    try:
        RunGraph(k8s_client=k8s_client).run_graph(graph_name)
    except Exception as e:
        assert not isinstance(e, CustomError)
        assert exc == e
