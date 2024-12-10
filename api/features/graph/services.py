from typing import Annotated

from fastapi import Depends

from external.kubernetes import KubernetesClient

from .models import EDAGRequest, GraphStatusDetails, RunGraphDetails, RunGraphParameters


class EDAGServices:
    def __init__(
        self, kubernetes_client: Annotated[KubernetesClient, Depends()]
    ) -> None:
        self._kubernetes_client = kubernetes_client

    @staticmethod
    async def create_edag(graph_name: str, graph: EDAGRequest) -> EDAGRequest:
        pass

    @staticmethod
    async def run_edag(
        graph_name: str, run_parameters: RunGraphParameters
    ) -> RunGraphDetails:
        pass

    @staticmethod
    async def get_edag_status(graph_name: str) -> GraphStatusDetails:
        pass
