from typing import Annotated, cast

from fastapi import APIRouter, Body, Depends, Path, Security
from fastapi.responses import JSONResponse

from auth.security import RBACSecurity
from models.auth import Role, User
from models.edag import EDAGRequest
from models.edagrun import EDAGRunResponse
from .services import EDAGServices

router = APIRouter(prefix="/api/v1/edag")

_EDAG_TAG = "EDAG"
_EDAG_EXECUTION_TAG = "EDAG Execution"


@router.post(
    "/",
    tags=[_EDAG_TAG],
    description="Create new EDAG",
)
async def create_edag(
    edag_request: Annotated[EDAGRequest, Body()],
    edag_services: Annotated[EDAGServices, Depends()],
    _user: Annotated[User, Security(RBACSecurity.verify)],
) -> None:
    await edag_services.create_edag(edag_request)


@router.post(
    "/{edagname}/run", tags=[_EDAG_EXECUTION_TAG], description="Execute an EDAG"
)
async def run_edag(
    edagname: Annotated[str, Path()],
    graph_services: Annotated[EDAGServices, Depends()],
    _user: Annotated[User, Security(RBACSecurity.verify)],
) -> EDAGRunResponse:
    run_response = await graph_services.run_edag(edagname)
    return cast(EDAGRunResponse, run_response)


@router.delete(
    "/{edagname}",
    tags=[_EDAG_TAG],
    description="Delete an EDAG and all associated runs. Admin only",
)
async def delete_edag(
    edagname: Annotated[str, Path()],
    _user: Annotated[
        User, Security(RBACSecurity.verify, scopes=[Role.KICKPLATE_ADMIN])
    ],
) -> JSONResponse:
    """Non functional, used for test for admin role"""
    return JSONResponse(status_code=500, content="Endpoint not implemented")
