from kubernetes import client, config as k_config
from kubernetes.dynamic import DynamicClient
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from src.error_handling import CustomError, HttpCodes
from src.config import config
from src.logger import LoggingLevel, Loggers


def validate_against_schema(json_schema:dict, json_def:str) -> tuple[bool, str]:
    try:
        # Check validity of user input against schema
        validate(instance=json_def, schema=json_schema)
    except ValidationError as e:
        # Invalid schema
        raise CustomError(
            message=f"Invalid execution graph input, schema error message: {e.message}",
            error_code=HttpCodes.USER_ERROR,
            logger=Loggers.USER_ERROR,
            logging_level=LoggingLevel.INFO
        ) 


def read_schema() -> dict:
    # Get schema path from config
    path = config.get(section="kube_config", key="schema_path")
    try:
        with open(path, "r") as fs:
            return json.loads(fs.read())
    except FileNotFoundError:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Schema File {path} not found",
            logging_level=LoggingLevel.WARNING
        ) 
    except IOError:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error reading schema",
            logging_level=LoggingLevel.WARNING
        ) 


def connect_to_kubenetes() -> DynamicClient:
    try:
        k_config.load_kube_config()
        return DynamicClient(client.ApiClient())
    except Exception as e:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error connecting to k8, error message {e.__repr__()}",
            # Critical as core functionality
            logging_level=LoggingLevel.CRITICAL
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
            logging_message=f"Error getting resource Kind: {kind} Error: {e.__repr__()}",
            logging_level=LoggingLevel.CRITICAL
        )
        
def get_co_client_api() -> client.CustomObjectsApi:
    connect_to_kubenetes()
    return client.CustomObjectsApi()
