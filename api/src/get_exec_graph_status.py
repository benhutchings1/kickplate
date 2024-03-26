import logging
import json
from kubernetes.client.exceptions import ApiException
from src import utils
from src.error_handling import CustomError, HttpCodes
from src.config import config
from src.logger import LoggingLevel, Loggers


def get_exec_graph_status(execution_id:str):
    """
    Gets the status of an execution graph
    Input:
        - execution_id (string) UUID of execution graph run
    
    Output:
        - (json) Description of execution
    """
    return extract_information(
        get_execution_description(execution_id=execution_id)
        )
    

def get_execution_description(execution_id:str):
    """
    Queries argo workflow API for relevant workflow 
    """
    
    client_api = utils.get_co_client_api()
    
    try:
        # Submit workflow get request
        return client_api.get_namespaced_custom_object(
                name=execution_id,
                group=config.get("workflow", "group"),
                version=config.get("workflow", "version"),
                plural=config.get("workflow", "plural"),
                namespace=config.get("kube_config", "namespace")
        )
    except ApiException as e:
        # Check for specific known errors        
        if json.loads(e.body)["code"] == 404:
            raise CustomError(
                message=f"Graph: {execution_id} not found",
                error_code=HttpCodes.NOT_FOUND,
                logger=Loggers.USER_ERROR,
                logging_level=LoggingLevel.INFO
            )
        else:
            # Unknown error, let top level error handler capture it
            raise e


def extract_information(exec_desc):
    # Get relevant graph information
    overall_labels = exec_desc["metadata"]["labels"]
    steps_desc = exec_desc["status"]["nodes"]
    
    # Pop DAG graph definition
    graph_name = exec_desc["metadata"]["name"]
    steps_desc.pop(graph_name, None)
    
    # Get overall information
    refined_info = {
        "overall": {
            "completed": overall_labels.get("workflows.argoproj.io/completed", None),
            "phase": overall_labels.get("workflows.argoproj.io/phase", None),
            "creation_time":exec_desc["metadata"].get("creationTimestamp", None),
        },
        "steps_status": {
            step: get_step_information(steps_desc[step], graph_name) for step in steps_desc.keys() 
        } 
    }
    
    # Log warning of not retrieving some values
    for attr in ["completed", "phase", "creation_time"]:
        if refined_info["overall"][attr] is None:
            logging.warning(f"failed to get '{attr}' for graph: {graph_name}")
    
    return refined_info

def get_step_information(steps_desc, graph_name):
    # get specific info
    step_info = {
        "name": steps_desc.get("displayName", None),
        "state": steps_desc.get("phase", None),
        "start_time": steps_desc.get("startedAt", None),
        "finish_time": steps_desc.get("finishedAt", None),
        "error_message": steps_desc.get("message", None)
    }
    
    # Warning log if some data was not retrieved
    for attr in ["name", "state"]:
        if step_info[attr] is None:
            logging.warning(f"failed to get '{attr}' for graph: {graph_name}")
    
    return step_info