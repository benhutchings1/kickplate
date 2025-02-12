from typing import Annotated, Any, cast

import kr8s
from fastapi import Depends
from kr8s.asyncio.objects import APIObject

from entity_builders.base import BaseEntityBuilder
from models.base import BaseResource

_NAMESPACE = "default"


def _get_api() -> kr8s.Api:
    """Wrap factory to stop parameters leaking through dependency injection to api route"""
    return kr8s.api()


class KubernetesClient:
    def __init__(self, api: Annotated[kr8s.Api, Depends(_get_api)]) -> None:
        self._client = api

    async def create_resource(
        self, resource_builder: BaseEntityBuilder, resource: BaseResource
    ) -> dict[str, Any]:
        manifest = resource_builder.build_manifest(resource, _NAMESPACE)
        manifest.api = self._client
        await manifest.create()
        return cast(dict[str, Any], manifest.raw)

    async def get_resource(
        self, resource_builder: BaseEntityBuilder, name: str
    ) -> APIObject:
        return await resource_builder.get_crd().get(name, namespace=_NAMESPACE)
