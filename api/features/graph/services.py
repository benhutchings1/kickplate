from typing import Annotated

from fastapi import Depends

from entity_builders.edag import EDAGBuilder
from entity_builders.edagrun import EDAGRunBuilder
from external.kubernetes import KubernetesClient

from models.edag import EDAGRequest
from models.status import GraphStatusDetails
from models.edagrun import EDAGRunResource, EDAGRunResponse


class EDAGServices:
    def __init__(
        self,
        kubernetes_client: Annotated[KubernetesClient, Depends()],
        edag_builder: Annotated[EDAGBuilder, Depends()],
        edag_run_builder: Annotated[EDAGRunBuilder, Depends()],
    ) -> None:
        self._kubernetes_client = kubernetes_client
        self._edag_builder = edag_builder
        self._edag_run_builder = edag_run_builder

    async def create_edag(self, graph_name: str, edag_request: EDAGRequest) -> None:
        edag_resource = self._edag_builder.build_resource(edag_request)
        await self._kubernetes_client.create_resource(self._edag_builder, edag_resource)

    async def run_edag(self, edag_name: str) -> EDAGRunResponse:
        edag_run_resource = EDAGRunResource(edagname=edag_name)
        edag_run_manifest = await self._kubernetes_client.create_resource(
            self._edag_run_builder, edag_run_resource
        )
        return EDAGRunResponse(id=edag_run_manifest["metadata"]["name"])

    async def get_edag_status(self, graph_name: str) -> GraphStatusDetails:
        raise NotImplementedError
