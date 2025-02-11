from typing import Any
import pytest
from entity_builders.edagrun import EDAGRunBuilder
from models.edagrun import (
    EDAG_RUN_API_VERSION,
    EDAG_RUN_KIND,
    EDAGRunRequest,
    EDAGRunResource,
)


@pytest.fixture
def edagrun_request() -> EDAGRunRequest:
    return EDAGRunRequest(edagname="myedag")


@pytest.fixture
def edagrun_resource() -> EDAGRunResource:
    return EDAGRunResource(edagname="myedag")


@pytest.fixture
def edagrun_manifest() -> dict[str, Any]:
    return {
        "kind": EDAG_RUN_KIND,
        "metadata": {"namespace": "testnamespace"},
        "apiVersion": EDAG_RUN_API_VERSION,
        "spec": {"edagname": "myedag"},
    }


def test_should_get_crd_definition() -> None:
    crd_def = EDAGRunBuilder.get_crd()
    assert crd_def.kind == EDAG_RUN_KIND
    assert crd_def.version == EDAG_RUN_API_VERSION


def test_should_edag_build_resource_from_request(
    edagrun_request: EDAGRunRequest, edagrun_resource: EDAGRunResource
) -> None:
    edag = EDAGRunBuilder()
    built_resource = edag.build_resource(edagrun_request)
    assert built_resource == edagrun_resource


def test_should_build_manifest_from_resource(
    edagrun_resource: EDAGRunResource, edagrun_manifest: dict[str, Any]
) -> None:
    edag = EDAGRunBuilder()
    built_manifest = edag.build_manifest(
        edagrun_resource, edagrun_manifest["metadata"]["namespace"]
    )
    raw_manifest = built_manifest.raw.to_dict()

    # Suffix is unknown, so do fine comparison on metadata
    expected_namespace = edagrun_manifest.pop("metadata")["namespace"]
    generated_metadata = raw_manifest.pop("metadata")
    generated_name: str = generated_metadata["name"]

    assert expected_namespace == generated_metadata["namespace"]
    assert generated_name.startswith(edagrun_resource.edagname)
    assert raw_manifest == edagrun_manifest
