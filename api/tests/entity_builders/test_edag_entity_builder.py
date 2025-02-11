from typing import Any
import pytest
from entity_builders.edag import EDAGBuilder
from models.edag import (
    EDAG_API_VERSION,
    EDAG_KIND,
    EDAGRequest,
    EDAGRequestStep,
    EDAGResource,
    EDAGStepResource,
)


@pytest.fixture
def edag_request() -> EDAGRequest:
    return EDAGRequest(
        graphname="testgraphname",
        steps=[
            EDAGRequestStep(
                stepname="step1",
                image="image1",
                replicas=1,
                env={"type": "value1"},
                args=["step1arg"],
                command=["step1command"],
            ),
            EDAGRequestStep(
                stepname="step2",
                image="image2",
                replicas=2,
                dependencies=["step2"],
                env={"type": "value2"},
                args=["step2arg"],
                command=["step2command"],
            ),
        ],
    )


@pytest.fixture
def edag_resource() -> EDAGResource:
    return EDAGResource(
        graphname="testgraphname",
        steps=[
            EDAGStepResource(
                stepname="step1",
                image="image1",
                replicas=1,
                dependencies=[],
                env={"type": "value1"},
                args=["step1arg"],
                command=["step1command"],
            ),
            EDAGStepResource(
                stepname="step2",
                image="image2",
                replicas=2,
                dependencies=["step1"],
                env={"type": "value2"},
                args=["step2arg"],
                command=["step2command"],
            ),
        ],
    )


@pytest.fixture
def edag_manifest() -> dict[str, Any]:
    return {
        "kind": EDAG_KIND,
        "apiVersion": EDAG_API_VERSION,
        "metadata": {"name": "testgraphname", "namespace": "testnamespace"},
        "spec": {
            "steps": {
                "step1": {
                    "image": "image1",
                    "replicas": 1,
                    "argument": ["step1arg"],
                    "envs": {"type": "value1"},
                    "command": ["step1command"],
                    "dependencies": [],
                },
                "step2": {
                    "image": "image2",
                    "replicas": 2,
                    "argument": ["step2arg"],
                    "envs": {"type": "value2"},
                    "command": ["step2command"],
                    "dependencies": ["step1"],
                },
            }
        },
    }


def test_should_get_crd_definition():
    crd_def = EDAGBuilder.get_crd()
    assert crd_def.kind == EDAG_KIND
    assert crd_def.version == EDAG_API_VERSION


def test_should_edag_build_resource_from_request(
    edag_request: EDAGRequest, edag_resource: EDAGResource
):
    edag = EDAGBuilder()
    built_resource = edag.build_resource(edag_request)
    assert built_resource == edag_resource


def test_should_build_manifest_from_resource(
    edag_resource: EDAGResource, edag_manifest: dict[str, Any]
):
    edag = EDAGBuilder()
    built_manifest = edag.build_manifest(
        edag_resource, edag_manifest["metadata"]["namespace"]
    )
    raw_manifest = built_manifest.raw.to_dict()
    assert raw_manifest == edag_manifest
