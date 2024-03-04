"""This module contains the top level API functions for the deployment engine API"""

from src import create_exec_graph, run_exec_graph, get_exec_graph_status
from src.error_handling import HttpCodes, CustomError, get_error_source


def create_execution_graph(json_def:dict):
    """
    Top level API endpoint for submitting an execution graph
    Inputs:
        - json_def (dict) JSON execution graph definition
    Outputs:
        - Success/Error HTTP Code
    """
    try:
        create_exec_graph.create_exec_graph(json_def)
    except CustomError as e:
        # Feedback about known errors
        raise e
    except Exception as error:
        # Catch unknown errors
        filename, line = get_error_source()
        # Raise soft error
        CustomError(
            message="An unknown error occured, please contact an admin",
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error: {type(error)} File:{filename} Line:{line}"
        ) 


def run_execution_graph(model_name:str):
    """
    Top level API function for running an execution graph, defined in create_execution_graph
    Inputs
        - model_name (str) execution graph name
    Output
        - Unique execution identifier
    """
    try:
        run_exec_graph.run_execution_graph(model_name)
    except CustomError:
        # Feedback about known errors
        pass
    except Exception as error:
        # Catch unknown errors
        filename, line = get_error_source()
        # Raise soft error
        CustomError(
            message="An unknown error occured, please contact an admin",
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error: {type(error)} File:{filename} Line:{line}"
        )


def get_execution_status(execution_id:str):
    """
    Top level API function for getting status of an execution graph
    Inputs
        - execution_id (str) execution identifier
    Output
        - (json) description of execution
    """
    try:
        get_exec_graph_status.get_exec_graph_status(execution_id)
    except CustomError:
        # Feedback about known errors
        pass
    except Exception as error:
        # Catch unknown errors
        filename, line = get_error_source()
        # Raise soft error
        CustomError(
            message="An unknown error occured, please contact an admin",
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error: {type(error)} File:{filename} Laine:{line}"
        )
