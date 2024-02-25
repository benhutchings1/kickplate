from src import utils
from src.error_handling import CustomError, HttpCodes
from kubernetes.dynamic.resource import ResourceInstance
from kubernetes.dynamic import DynamicClient
from kubernetes import client
from kubernetes.dynamic.exceptions import ApiException
import json
from random import choices
from string import ascii_lowercase

def run_execution_graph(graph_name, api_version:str="test.deploymentengine.com/v1",
                       namespace:str="default") -> str:
    # Get graph defintion from cluster
    graph_def = get_graph_definition(graph_name, api_version=api_version, namespace=namespace)

    # generate workflow
    workflow = generate_workflow(graph_name, graph_def)
    
    # submit workflow and return workflow name
    return submit_workflow(workflow)   


def get_graph_definition(graph_name, api_version, namespace, kind:str='ExecutionGraph') -> dict:
    # Get model graphs resource
    resource_type:DynamicClient = utils.get_execgraph_resource(api_version, kind=kind)
    
    try:
        resources:ResourceInstance = resource_type.get(namespace=namespace)
    except Exception as e:
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Tried to get graph resource, message: {e.message}"
        )
    
    # Search for graph    
    for item in resources["items"]:
        if graph_name == item["metadata"]["name"]:
            return item
    
    raise CustomError(
        message="execution graph '{graph_name}' not found",
        error_code=HttpCodes.USER_ERROR
    )
    
    
def generate_workflow(graph_name:str, step_definitions:list[dict]) -> dict:
    # Format steps and DAG for execution
    templates = []
    for step_def in step_definitions["spec"]["steps"]:
        templates.append(create_template(step_def))
    templates.append(create_dag(step_definitions))
    
    # Generate name
    
    return {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {
            "name": generate_name_suffix(graph_name, length=5)
            },
            "spec": {
                "entrypoint": "dag-workflow",
                "templates": templates                
            }
        }

def generate_name_suffix(graph_name:str, length:int) -> str:
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
        
    
def submit_workflow(workflow:dict[str], group:str="argoproj.io",  version:str="v1alpha1",
                    plural:str="workflows", namespace:str="argo") -> str:
    try:
        client.CustomObjectsApi().create_namespaced_custom_object(
            group=group,
            version=version,
            plural=plural,
            body=workflow,
            namespace=namespace
        )
        return workflow['metadata']['name']
    except ApiException as e:
        # Check for specific known errors
        if json.loads(e.body)["code"] == 409:
            raise CustomError(
                error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                logging_message=f"'{workflow['metadata']['name']}' already exists"
            ) from None 
        else:
            # Unknown error, let top level error handler capture it
            raise e