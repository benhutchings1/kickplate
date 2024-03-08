"""This module contains the top level API functions for the deployment engine API"""
from typing import Coroutine, Callable, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute, APIRouter
from starlette.responses import Response
from src import create_exec_graph, run_exec_graph, get_exec_graph_status, api_schemas
from src.error_handling import HttpCodes, error_handler, catch_all_exceptions
import uvicorn

# Start API
app = FastAPI()
app.middleware('http')(catch_all_exceptions)


@app.post("/create_graph")
async def create_execution_graph(graph_def:api_schemas.CreateExecGraphInput) -> api_schemas.CreateExecGraphOutput:
    """
    Top level API endpoint for submitting an execution graph\n  
    Inputs:\n
        - graph_def (JSON): JSON execution graph definition\n
    """
   
    # Return OK status
    return JSONResponse(
        status_code=HttpCodes.OK.value,
        content=create_exec_graph.create_exec_graph(graph_def)
    )
    

@app.post("/run_graph/{model_name}")
async def run_execution_graph(model_name:str) -> api_schemas.RunExecGraphOutput:
    """
    Top level API function for running an execution graph, defined in create_execution_graph\n
    Inputs\n
        - model_name (str): execution graph name\n
    Output\n
        - execution_id (str): Unique execution identifier\n
    """
    # Run execution graph
    return JSONResponse(
        status_code=HttpCodes.OK.value,
        content=run_exec_graph.run_execution_graph(model_name)
    )



@app.get("/get_status/{execution_id}")
async def get_execution_status(execution_id:str) -> api_schemas.ExecGraphStatusOutput:
    """
    Top level API function for getting status of an execution graph\n
    Inputs\n
        - execution_id (str): execution identifier\n
    Output\n
        - execution_description (json): description of execution\n
    """
    return JSONResponse(
        status_code=HttpCodes.OK.value,
        content=get_exec_graph_status.get_exec_graph_status(execution_id)
    )


@app.get("/")
async def health_check() -> None:
    """Health check for getting API status"""
    return JSONResponse(status_code=HttpCodes.OK.value, content={"status": "ok"})


# @app.exception_handler(Exception)
# def all_exception_handler(__:Request, exc:Exception):
#     formatted_error = error_handler(exc)

#     return JSONResponse(
#         status_code=formatted_error.error_code.value,
#         content={"error": formatted_error.message}
#     )


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)