from external.cluster import KubernetesClient
from .dtos import ExecutionGraph, RunGraphParameters, RunGraphDetails, GraphStatusDetails


class GraphServices:
    def __init__(self) -> None:
        self._kubernetes_client = KubernetesClient()

    @staticmethod
    async def create_execution_graph(graph_name: str, graph: ExecutionGraph) -> ExecutionGraph:
        pass

    @staticmethod
    async def run_execution_graph(graph_name: str, run_parameters: RunGraphParameters) -> RunGraphDetails:
        pass

    @staticmethod
    async def get_execution_graph_status(graph_name: str) -> GraphStatusDetails:
        pass
