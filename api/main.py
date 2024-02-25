from src import create_exec_graph, run_exec_graph
from src.error_handling import HttpCodes, CustomError, get_error_source

def create_execution_graph(json_def:dict):
    # Top level API endpoint for submitting an execution graph
    try:
        create_exec_graph.create_exec_graph(json_def)
    except CustomError as e:
        # Feedback about known errors
        raise e
    except Exception as error:
        # Catch unknown errors
        filename, line = get_error_source()
        raise CustomError(
            message="An unknown error occured, please contact an admin",
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error: {type(error)} File:{filename} Line:{line}"
        )


def run_execution_graph(model_name:str):
    # Top level API function for running an existing execution graph
    try:
        run_exec_graph.run_execution_graph(model_name)
    except CustomError:
        # Feedback about known errors
        pass
    except Exception as error:
        # Catch unknown errors
        filename, line = get_error_source()
        raise CustomError(
            message="An unknown error occured, please contact an admin",
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error: {type(error)} File:{filename} Line:{line}"
        )