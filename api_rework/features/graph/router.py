from fastapi import APIRouter, Path, Depends, Body
from typing import Annotated
from .dtos import ExecutionGraph, RunGraphDetails, RunGraphParameters, GraphStatusDetails
from .services import GraphServices
_GRAPH_TAG = "Graphs"

router = APIRouter(
    prefix="/api/v1/graph",
    tags=[_GRAPH_TAG],
)


@router.post("/create/{graph_name}")
async def create_execution_graph(
    graph_name: Annotated[str, Path()],
    graph: Annotated[ExecutionGraph, Body()],
    graph_services: Annotated[GraphServices, Depends()]
) -> ExecutionGraph:
    return await graph_services.create_execution_graph(
        graph_name, graph
    )


@router.post("/run/{graph_name}")
async def run_execution_graph(
    graph_name: Annotated[str, Path()],
    run_parameters: Annotated[RunGraphParameters, Body()],
    graph_services: Annotated[GraphServices, Depends()]
) -> RunGraphDetails:
    return await graph_services.run_execution_graph(graph_name, run_parameters)


@router.get("/{graph_name}")
async def get_graph_status(
    graph_name: Annotated[str, Path()],
    graph_services: Annotated[GraphServices, Depends()]
) -> GraphStatusDetails:
    return await graph_services.run_execution_graph(graph_name)
