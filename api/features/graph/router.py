from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, Path, Request, Security
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes

from auth.models import User, Scopes
from auth.security import RBACSecurity
from settings import settings

from .models import EDAGRequest, GraphStatusDetails, RunGraphDetails, RunGraphParameters
from .services import EDAGServices

router = APIRouter(
    prefix="/api/v1/graph",
)

_EDAG_TAG = "EDAG"
_EDAG_EXECUTION_TAG = "EDAG Execution"


@router.post(
    "/{edag_name}",
    tags=[_EDAG_TAG],
    description="Create new EDAG",
)
async def create_edag(
    edag_name: Annotated[str, Path()],
    graph: Annotated[EDAGRequest, Body()],
    graph_services: Annotated[EDAGServices, Depends()],
) -> EDAGRequest:
    return await graph_services.create_edag(edag_name, graph)


@router.put("/{edag_name}", tags=[_EDAG_TAG], description="Update an existing EDAG")
async def update_edag(
    edag_name: Annotated[str, Path()],
    updated_graph: Annotated[EDAGRequest, Body()],
    graph_services: Annotated[EDAGServices, Depends()],
) -> EDAGRequest:
    raise NotImplementedError()


@router.get("/{edag_name}", tags=[_EDAG_TAG], description="Fetch an existing EDAG")
async def get_edag(
    edag_name: Annotated[str, Path()],
    graph_services: Annotated[EDAGServices, Depends()],
) -> EDAGRequest:
    raise NotImplementedError()


@router.delete("/{edag_name}", tags=[_EDAG_TAG], description="Delete an existing EDAG")
async def delete_edag(
    edag_name: Annotated[str, Path()],
    graph_services: Annotated[EDAGServices, Depends()],
) -> EDAGRequest:
    raise NotImplementedError()


@router.post("/{run_id}/run", tags=[_EDAG_EXECUTION_TAG], description="Execute an EDAG")
async def run_edag(
    run_id: Annotated[str, Path()],
    run_parameters: Annotated[RunGraphParameters, Body()],
    graph_services: Annotated[EDAGServices, Depends()],
) -> RunGraphDetails:
    return await graph_services.run_edag(run_id, run_parameters)


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.AUTH_AUTH_URL,
    tokenUrl=settings.AUTH_TOKEN_URL,
)


@router.get(
    "/{run_id}/run",
    tags=[_EDAG_EXECUTION_TAG],
    description="Get the status of an existing EDAG run",
)
async def get_edag_status(
    run_id: Annotated[str, Path()],
    graph_services: Annotated[EDAGServices, Depends()],
) -> GraphStatusDetails:
    return await graph_services.get_edag_status(run_id)
