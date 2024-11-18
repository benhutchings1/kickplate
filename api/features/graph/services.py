from external.cluster import KubernetesClient
from .models import EDAG, RunGraphParameters, RunGraphDetails, GraphStatusDetails


class GraphServices:
    def __init__(self) -> None:
        self._kubernetes_client = KubernetesClient()

    @staticmethod
    async def create_edag(graph_name: str, graph: EDAG) -> EDAG:
        pass

    @staticmethod
    async def run_edag(graph_name: str, run_parameters: RunGraphParameters) -> RunGraphDetails:
        pass

    @staticmethod
    async def get_edag_status(graph_name: str) -> GraphStatusDetails:
        pass
