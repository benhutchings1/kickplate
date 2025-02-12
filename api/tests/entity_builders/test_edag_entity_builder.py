from typing import Any

from entity_builders.edag import EDAGBuilder
from models.edag import EDAG_API_VERSION, EDAG_KIND, EDAGRequest, EDAGResource


def test_should_get_crd_definition():
    crd_def = EDAGBuilder.get_crd()
    assert crd_def.kind == EDAG_KIND
    assert crd_def.version == EDAG_API_VERSION


def test_should_edag_build_resource_from_request(
    edag_request: EDAGRequest, edag_run_resource: EDAGResource
):
    edag = EDAGBuilder()
    built_resource = edag.build_resource(edag_request)
    assert built_resource == edag_run_resource


def test_should_build_manifest_from_resource(
    edag_run_resource: EDAGResource, edag_manifest: dict[str, Any]
):
    edag = EDAGBuilder()
    built_manifest = edag.build_manifest(
        edag_run_resource, edag_manifest["metadata"]["namespace"]
    )
    raw_manifest = built_manifest.raw.to_dict()
    assert raw_manifest == edag_manifest
