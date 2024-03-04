from kubernetes import client, config
from kubernetes.dynamic import DynamicClient
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from src.error_handling import CustomError, HttpCodes


def validate_against_schema(json_schema:dict, json_def:str) -> tuple[bool, str]:
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
    try:
        with open(path, "r") as fs:
            return json.loads(fs.read())
    except FileNotFoundError:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"File {path} not found"
        ) 
    except IOError:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f""
        ) 


def connect_to_kubenetes() -> DynamicClient:
    try:
        config.load_kube_config()
        return DynamicClient(client.ApiClient())
    except Exception as e:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error connecting to k8, error message {e.message}"
        )

def get_resource(api_version, kind) -> DynamicClient:
    # Get dynamic client
    dy_client = connect_to_kubenetes()
    
    # Try get ExecutionGraph resource
    try:
        return dy_client.resources.get(api_version=api_version, kind=kind)
    except Exception as e:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=e.message
        )
        
def get_co_client_api() -> client.CustomObjectsApi:
    connect_to_kubenetes()
    return client.CustomObjectsApi()
