from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from auth.auth_flow import oauth_scheme
from com_utils.error_handling import catch_all_exceptions
from com_utils.http import HttpCodes
from com_utils.logger import modify_uvicorn_logging_config
from config import ApiSettings
from api.external.cluster import K8Client

# Import routes functionality
from routes.create_graph.create_exec_graph import CreateExecGraph
from routes.create_graph.create_exec_graph import (
    ResponseModel as CreateGraphResponseModel,
)
from routes.graph_status.graph_status import GraphStatus
from routes.graph_status.graph_status_model import (
    GraphStatusModel as GraphStatusReponseModel,
)
from routes.run_graph.run_exec_graph import ResponseModel as RunGraphResponseModel
from routes.run_graph.run_exec_graph import RunGraph

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
app.middleware("http")(catch_all_exceptions)


@app.post("/graph/create_graph")
async def create_execution_graph(
    graph_def: dict,
    token: Annotated[str, Depends(oauth_scheme)],
    kubernetes_client: Annotated[K8Client, Depends(K8Client)],
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
        content={
            "graphname": CreateExecGraph(k8s_client=kubernetes_client).submit_graph(
                graph_def
            )
        },
    )


@app.post("/graph/{model_name}")
async def run_execution_graph(
    model_name: str,
    token: Annotated[str, Depends(oauth_scheme)],
    kubernetes_client: Annotated[K8Client, Depends(K8Client)],
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
        status_code=HttpCodes.OK.value,
        content={
            "execution_id": RunGraph(k8s_client=kubernetes_client).run_graph(model_name)
        },
    )


@app.get("/graph/{execution_id}")
async def get_execution_status(
    execution_id: str,
    token: Annotated[str, Depends(oauth_scheme)],
    kubernetes_client: Annotated[K8Client, Depends(K8Client)],
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
        content=GraphStatus(k8s_client=kubernetes_client).get_graph_status(
            execution_id
        ),
    )


@app.get("/")
async def health_check() -> None:
    """Health check for getting API status"""
    return JSONResponse(status_code=HttpCodes.OK.value, content={"status": "ok"})


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8000, reload=True)
