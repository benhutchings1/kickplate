from fastapi import APIRouter, Path, Depends, Body
from typing import Annotated
from .models import EDAG, RunGraphDetails, RunGraphParameters, GraphStatusDetails
from .services import GraphServices
_GRAPH_TAG = "EDAGs"

router = APIRouter(
    prefix="/api/v1/graph",
    tags=[_GRAPH_TAG],
)


@router.post("/create/{graph_name}")
async def create_edag(
    graph_name: Annotated[str, Path()],
    graph: Annotated[EDAG, Body()],
    graph_services: Annotated[GraphServices, Depends()]
) -> EDAG:
    return await graph_services.create_edag(
        graph_name, graph
    )


@router.post("/run/{run_id}")
async def run_edag(
    run_id: Annotated[str, Path()],
    run_parameters: Annotated[RunGraphParameters, Body()],
    graph_services: Annotated[GraphServices, Depends()]
) -> RunGraphDetails:
    return await graph_services.run_edag(run_id, run_parameters)


@router.get("/run/{run_id}")
async def get_edag_status(
    run_id: Annotated[str, Path()],
    graph_services: Annotated[GraphServices, Depends()]
) -> GraphStatusDetails:
    return await graph_services.get_edag_status(run_id)
