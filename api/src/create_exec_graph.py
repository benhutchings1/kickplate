from kubernetes.client.exceptions import ApiException
from kubernetes.dynamic.exceptions import ConflictError
from src.error_handling import CustomError, HttpCodes
import json
from src import utils
import re

def create_exec_graph(json_def:dict, api_version:str="test.deploymentengine.com/v1",
                       namespace:str="default") -> None:
    # Read in schema
    schema = utils.read_schema("src/exec_graph.schema.json")

    # Check validity from schema, will raise error if invalid
    utils.validate_against_schema(json_schema=schema,
                                          json_def=json_def)

    # Check graph name is valid, will raise error if invalid
    validate_name(json_def["graphname"])
    
    # Add meta data to make valid execgraph request
    exec_graph_definition = format_request(json_def, api_version=api_version)
    
    # Submit execgraph
    submit_execgraph(
        exec_graph=exec_graph_definition,
        namespace=namespace,
        api_version=api_version
    )
        

def format_request(json_def:dict, api_version:str) -> dict:
    try:
        # Structure ExecutionGraph resource request
        return {
            "apiVersion": api_version,
            "kind": "ExecutionGraph",
            "metadata": {
                "name": json_def["graphname"]
            },
            "spec": {
                "steps": json_def["steps"]
            } 
        }
    except KeyError as e:
        raise CustomError(
            message=f"Data {e} missing from graph definition",
            error_code=HttpCodes.USER_ERROR
            ) from None


def validate_name(execgraph_name:str) -> None:
    # Check graph name against regex
    regex_engine = re.compile('[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*')
    if not bool(regex_engine.match(execgraph_name)):
        raise CustomError(
            message=f"graph name [{execgraph_name}] \
                must consist of lower case alphanumeric characters, '-', or '.', and must start/end with an alphanumeric character",
            error_code=HttpCodes.USER_ERROR
        ) from None


def submit_execgraph(exec_graph:dict, namespace:str,
                     api_version:str, kind:str='ExecutionGraph') -> None:
    # Get resource
    resource = utils.get_execgraph_resource(api_version=api_version, kind=kind)    
    
    # Try submit execgraph
    try:
        # Attempt to create graph resource
        resource.create(body=exec_graph, namespace=namespace)
    except ApiException as e:
        # Check for specific known errors        
        if json.loads(e.body)["code"] == 409:
            raise CustomError(
                message=f"{exec_graph['metadata']['name']} already exists",
                error_code=HttpCodes.CONFLICT
            ) from None 
        else:
            # Unknown error, let top level error handler capture it
            raise e