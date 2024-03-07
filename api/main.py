"""This module contains the top level API functions for the deployment engine API"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src import create_exec_graph, run_exec_graph, get_exec_graph_status, api_schemas
from src.error_handling import HttpCodes, error_handler, CustomError

# Start API
app = FastAPI()

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


@app.exception_handler(CustomError)
def custom_error_handler(__:Request, exc:CustomError) -> api_schemas.ErrorStatusOutput:
    return JSONResponse(
        status_code=exc.error_code.value,
        content={"error": exc.message}
    )


@app.exception_handler(Exception)
def all_exception_handler(__:Request, exc:Exception):
    error_handler(exc)