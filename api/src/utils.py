"""Common utility functions, accessible over the whole project"""
import json
from kubernetes import client, config
from kubernetes.dynamic import DynamicClient, ResourceInstance
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from src.error_handling import CustomError, HttpCodes


def validate_against_schema(json_schema:dict, json_def:str) -> None:
    """
    Validates user defined graph against schema for input validation. 
    Raises an error if exec graph is invalid, otherwise returns nothing 
    Inputs:
        - json_schema (dict) JSON schema
        - json_def (dict) users JSON definition of exec graph
    """
    try:
        # Check validity of user input against schema
        validate(instance=json_def, schema=json_schema)
    except ValidationError as e:
        # Invalid schema
        raise CustomError(
            message=f"Invalid execution graph input, schema error message: {e.message}",
            error_code=HttpCodes.USER_ERROR
        ) from None


def read_schema(path:str) -> dict:
    """
    Read JSON schema for execution graph definitions
    Inputs:
        - path (str) path to .json file exec graph schema
    
    Outputs:
        - (dict) contents of schema file
    """
    try:
        with open(path, "r", encoding="utf-8") as fs:
            return json.loads(fs.read())
    except FileNotFoundError as e:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"File {path} not found"
        ) from e
    except IOError as e:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"IOError, error message: {e}"
        ) from e


def connect_to_kubenetes() -> DynamicClient:
    """
    Connects to kubernetes cluster to perform actions. Uses predefined kubernetes config
    (default found in ~/.kube) to authorise and connect
    
    Outputs:
        - (DynamicClient) client object connected to the cluster
    """
    try:
        config.load_kube_config()
        return DynamicClient(client.ApiClient())
    except Exception as e:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error connecting to k8, error message {e}"
        ) from e


def get_execgraph_resource(api_version, kind) -> ResourceInstance:
    """
    Uses DynamicClient to retrieve the ExecutionGraph resource
    input:
        - api_version (str) version of API to interrogate
        - kind (str) singular resource name
    
    Output:
        - (ResourceInstance) resource to fill 
    """
    # Get dynamic client
    dy_client = connect_to_kubenetes()
    # Try get ExecutionGraph resource
    try:
        return dy_client.resources.get(api_version=api_version, kind=kind)
    except Exception as e:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=str(e)
        ) from e
        