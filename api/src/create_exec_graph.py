from kubernetes.client.exceptions import ApiException
from src.error_handling import CustomError, HttpCodes
from src.config import config
import json
from src import utils
import re

def create_exec_graph(json_def:dict) -> None:
    # Read in schema
    schema = utils.read_schema("config/exec_graph.schema.json")

    # Check validity from schema, will raise error if invalid
    utils.validate_against_schema(json_schema=schema,
                                    json_def=json_def)

    # Check graph name is valid, will raise error if invalid
    validate_name(json_def["graphname"])
    
    # Add meta data to make valid execgraph request
    exec_graph_definition = format_request(
        json_def=json_def, 
        api_version=config.get()
    )
    
    # Submit execgraph
    submit_execgraph(
        exec_graph=exec_graph_definition,
        namespace=config.get(section="kube_config", key="namespace"),
        api_version=config.get(section="exegraph", key="api_version")
    )
        

def format_request(json_def:dict) -> dict:
    try:
        # Structure ExecutionGraph resource request
        return {
            "apiVersion": config.get("execgraph", "api_version"),
            "kind": config.get("execgraph", "kind"),
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


def submit_execgraph(exec_graph:dict) -> None:
    # Get resource
    resource = utils.get_resource(api_version=config.get("execgraph", "api_version"),
                                  kind=config.get("execgraph", "kind")) 
    
    # Try submit execgraph
    try:
        # Attempt to create graph resource
        resource.create(body=exec_graph, namespace=config.get("kube_config", "namespace"))
    except ApiException as e:
        # Check for specific known errors        
        if str(json.loads(e.body)["code"]) == str(409):
            raise CustomError(
                message=f"{exec_graph['metadata']['name']} already exists",
                error_code=HttpCodes.CONFLICT
            ) from e 
        else:
            # Unknown error, let top level error handler capture it
            raise e