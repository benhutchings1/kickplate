import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
from config import ApiSettings
from auth.auth_flow import oauth_scheme
from com_utils.http import HttpCodes
from com_utils.logger import modify_uvicorn_logging_config
from com_utils.error_handling import catch_all_exceptions

# Import routes functionality
from routes.create_graph.create_exec_graph import (
    CreateExecGraph,
    ResponseModel as CreateGraphResponseModel,
)
from routes.graph_status.graph_status import GraphStatus
from routes.graph_status.graph_status_model import (
    GraphStatusModel as GraphStatusReponseModel,
)
from routes.run_graph.run_exec_graph import (
    RunGraph,
    ResponseModel as RunGraphResponseModel,
)

app = FastAPI(
    swagger_ui_init_oauth={
        "appName": "deployment_engine",
        "clientId": ApiSettings.auth_client_id,
        "scopes": ApiSettings.auth_scope.split(" "),
        "usePkceWithAuthorizationCodeGrant": True,
    },
    lifespan=modify_uvicorn_logging_config,
)
# Exception catcher
# app.middleware("http")(catch_all_exceptions)


@app.post("/graph/create_graph")
async def create_execution_graph(
    graph_def: dict, token: Annotated[str, Depends(oauth_scheme)]
) -> CreateGraphResponseModel:
    """
    Top level API endpoint for submitting an execution graph\n
    Inputs:\n
        - graph_def (JSON): JSON execution graph definition\n
        - token (str): Bearer token provided by Azure Entra ID\n
    """

    # Return OK status
    return JSONResponse(
        status_code=HttpCodes.OK.value,
        content={"graphname": CreateExecGraph(graph_def)},
    )


@app.post("/graph/{model_name}")
async def run_execution_graph(
    model_name: str, token: Annotated[str, Depends(oauth_scheme)]
) -> RunGraphResponseModel:
    """
    Top level API function for running an execution graph,
        defined in create_execution_graph\n
    Inputs\n
        - model_name (str): execution graph name\n
        - token (str): Bearer token provided by Azure Entra ID
    Output\n
        - execution_id (str): Unique execution identifier\n
    """
    # Run execution graph
    return JSONResponse(
        status_code=HttpCodes.OK.value, content={"execution_id": RunGraph(model_name)}
    )


@app.get("/graph/{execution_id}")
async def get_execution_status(
    execution_id: str, token: Annotated[str, Depends(oauth_scheme)]
) -> GraphStatusReponseModel:
    """
    Top level API function for getting status of an execution graph\n
    Inputs\n
        - execution_id (str): execution identifier\n
        - token (str): Bearer token provided by Azure Entra ID
    Output\n
        - execution_description (json): description of execution\n
    """
    return JSONResponse(
        status_code=HttpCodes.OK.value,
        content=GraphStatus(execution_id),
    )


@app.get("/")
async def health_check() -> None:
    """Health check for getting API status"""
    return JSONResponse(status_code=HttpCodes.OK.value, content={"status": "ok"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=7000, reload=True)
