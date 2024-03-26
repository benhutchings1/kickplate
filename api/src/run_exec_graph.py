import json
from random import choices
from string import ascii_lowercase
from kubernetes.dynamic.resource import ResourceInstance
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import ApiException
from src import utils
from src.error_handling import CustomError, HttpCodes
from src.config import config
from src.logger import LoggingLevel, Loggers

def run_execution_graph(graph_name) -> str:
    # Get graph defintion from cluster
    graph_def = get_graph_definition(graph_name)

    # generate workflow
    workflow = generate_workflow(graph_name, graph_def)
    
    # submit workflow and return workflow name
    return submit_workflow(workflow)   


def get_graph_definition(graph_name) -> dict:
    # Get model graphs resource
    resource_type:DynamicClient = utils.get_resource(api_version=config.get("execgraph", "api_version"),
                                                     kind=config.get("execgraph", "kind"))
    try:
        resources:ResourceInstance = resource_type.get(namespace=config.get("kube_config", "namespace"))
    except Exception as e:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Tried to get graph resource, message: {e.__repr__()}",
            logging_level=LoggingLevel.WARNING
        )
    
    # Search for graph    
    for item in resources["items"]:
        if graph_name == item["metadata"]["name"]:
            return item
    
    raise CustomError(
        message="execution graph '{graph_name}' not found",
        error_code=HttpCodes.USER_ERROR,
        logger=Loggers.USER_ERROR,
        logging_level=LoggingLevel.INFO
    )
    
    
def generate_workflow(graph_name:str, step_definitions:list[dict]) -> dict:
    # Format steps and DAG for execution
    templates = []
    for step_def in step_definitions["spec"]["steps"]:
        templates.append(create_template(step_def))
    templates.append(create_dag(step_definitions))
    
    # Generate name
    
    return {
            "apiVersion": config.get("workflow", "api_version"),
            "kind": config.get("workflow", "kind"),
            "metadata": {
            "name": generate_name_suffix(graph_name, length=5)
            },
            "spec": {
                "entrypoint": "dag-workflow",
                "templates": templates     
            }
        }

def generate_name_suffix(graph_name:str, length:int) -> str:
    """Adds *length* lowercase ascii characters to end of graph_name"""
    return graph_name + "-" + ''.join(choices(ascii_lowercase, k=length))


def create_template(sd) -> dict:
    return {
          "name": sd["stepname"] + "-template",
          "container": {
            "image": sd["image"],
            "command": sd["command"],
            "args": sd["args"]
          }
        }

def create_dag(sd) -> dict:
    tasks = []
    for step in sd["spec"]["steps"]:
        tasks.append({
            "name": step["stepname"],
            "template": step["stepname"]+"-template",
            "dependencies": step["dependencies"]
        })
    return {
        "name": "dag-workflow",
        "dag": {
            "tasks": tasks
        }
    }
        
    
def submit_workflow(workflow:dict[str]) -> str:
    try:
        utils.get_co_client_api().create_namespaced_custom_object(
            group=config.get("workflow", "group"),
            version=config.get("workflow", "version"),
            plural=config.get("workflow", "plural"),
            namespace=config.get("kube_config", "namespace"),
            body=workflow
        )
        return workflow['metadata']['name']
    except ApiException as e:
        # Check for specific known errors
        if json.loads(e.body)["code"] == 409:
            raise CustomError(
                error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                logging_message=f"'{workflow['metadata']['name']}' already exists",
                logger=Loggers.USER_ERROR,
                logging_level=LoggingLevel.INFO
            )
        else:
            # Unknown error, let top level error handler capture it
            raise e