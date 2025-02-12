from typing import Annotated, cast

from fastapi import APIRouter, Body, Depends, Path
from fastapi.security import OAuth2AuthorizationCodeBearer

from models.edag import EDAGRequest
from models.edagrun import EDAGRunResponse
from models.status import GraphStatusDetails
from settings import settings

from .services import EDAGServices

router = APIRouter(
    prefix="/api/v1/edag",
)

_EDAG_TAG = "EDAG"
_EDAG_EXECUTION_TAG = "EDAG Execution"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.AUTH_AUTH_URL,
    tokenUrl=settings.AUTH_TOKEN_URL,
)


@router.post(
    "/",
    tags=[_EDAG_TAG],
    description="Create new EDAG",
)
async def create_edag(
    edag_request: Annotated[EDAGRequest, Body()],
    edag_services: Annotated[EDAGServices, Depends()],
) -> None:
    await edag_services.create_edag(edag_request)


@router.post(
    "/{edagname}/run", tags=[_EDAG_EXECUTION_TAG], description="Execute an EDAG"
)
async def run_edag(
    edagname: Annotated[str, Path()],
    graph_services: Annotated[EDAGServices, Depends()],
) -> EDAGRunResponse:
    run_response = await graph_services.run_edag(edagname)
    return cast(EDAGRunResponse, run_response)


@router.get(
    "/{run_id}/run",
    tags=[_EDAG_EXECUTION_TAG],
    description="Get the status of an existing EDAG run",
)
async def get_edag_status(
    run_id: Annotated[str, Path()],
    graph_services: Annotated[EDAGServices, Depends()],
) -> GraphStatusDetails:
    status = await graph_services.get_edag_status(run_id)
    return cast(GraphStatusDetails, status)
