from kubernetes.client.exceptions import ApiException
import json
from src import utils, kube
import re

def create_exec_graph(json_def:dict, api_version:str="test.deploymentengine.com/v1",
                       namespace:str="default") -> tuple[bool, str]:
    # Read in schema
    with open("src/exec_graph.schema.json", "r") as fs:
        schema = json.load(fs)
    
    # Check validity from schema
    valid = utils.validate_against_schema(json_schema=schema,
                                          json_def=json_def)
    if not valid[0]:
        return valid

    # Check graph name is valid
    regex_engine = re.compile('[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*')
    if not bool(regex_engine.match(json_def["graphname"])):
        return (False, "graph name must consist of lower case alphanumeric characters, '-', or '.', and must start/end with an alphanumeric character")

    # Add meta data to make valid execgraph request
    exec_graph_definition = format_request(json_def, api_version=api_version)
    
    # Create deployment
    dy_client = kube.connect_to_kubenetes()
    resource = dy_client.resources.get(api_version='test.deploymentengine.com/v1', kind='ExecutionGraph')
    try:
        # Attempt to create graph resource
        resource.create(body=exec_graph_definition, namespace=namespace)
        return (True, True)
    except ApiException as e:
        # Format error response
        error = json.loads(e.body)
        return (False, f"Code: {error['code']}, Message: {error['message']}")
        

def format_request(json_def:dict, api_version:str) -> dict:
    # Add metadata required for creating ExecutionGraph resource
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