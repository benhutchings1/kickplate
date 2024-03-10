from enum import Enum
from traceback import extract_stack
from os import path
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi import Request


class CustomError(Exception):
    def __init__(self, error_code, message=None, logging_message=None) -> None:        
        self.message = message
        self.logging_message = logging_message
        
        # Check error code
        if not isinstance(error_code, HttpCodes):
            # Get file and line of caller from stack trace
            filename, line = get_error_source(4)
            
            # Alter error to match new error
            self.error_code = HttpCodes.INTERNAL_SERVER_ERROR
            self.logging_message=f"File: {filename} Line: {line} tried to use non enumerated error code [{error_code}]"

        self.error_code = error_code
        
        # Set error message if internal server error, but require internal logging message
        if self.message is None and error_code is HttpCodes.INTERNAL_SERVER_ERROR:
            if self.logging_message is None:
                filename, line = get_error_source(6)
                self.error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                self.logging_message=f"File: {filename} Line: {line} raised internal server error without an logging message"

            self.message = "Internal server error"
        
        
        # if no logging message is given then revert to using main message
        if self.logging_message is None:
            self.logging_message = message
        
        # TODO: While logging not setup, print message
        print("LOGGING MESSAGE: ", self.logging_message)
    
    def __str__(self) -> str:
        return self.message


class HttpCodes(Enum):
    """Accepted HTTP Codes"""
    OK=status.HTTP_200_OK
    CREATED=status.HTTP_201_CREATED
    ACCEPTED=status.HTTP_202_ACCEPTED
    USER_ERROR=status.HTTP_400_BAD_REQUEST
    USER_UNAUTHORISED=status.HTTP_401_UNAUTHORIZED
    NOT_FOUND=status.HTTP_404_NOT_FOUND
    CONFLICT=status.HTTP_409_CONFLICT
    INTERNAL_SERVER_ERROR=status.HTTP_500_INTERNAL_SERVER_ERROR
    TOO_LARGE=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    TOO_MANY_REQUESTS=status.HTTP_429_TOO_MANY_REQUESTS


# Leave in error_handling to avoid circular import issues
def get_error_source(depth:int=3) -> tuple[str, str]:
    """Error utility function to get n_depth caller in stack trace"""
    try:
        # Get file and line of caller from stack trace
        stack_item = list(extract_stack())[-1 * depth]
        __, filename = path.split(stack_item.filename)
        line = stack_item.lineno
    except IndexError:
        # Try again with parent if there is no grandparent called 
        # Get file and line of caller from stack trace
        stack_item = list(extract_stack())[-1 * (depth + 1)]
        __, filename = path.split(stack_item.filename)
        line = stack_item.lineno
    
    return (filename, line)


def error_handler(error: Exception):
    if isinstance(error, CustomError):
        return error
    else:
        # Catch unknown errors
        filename, line = get_error_source(4)
        # Raise soft error
        return CustomError(
            message="An unexpected error occured, please contact an admin",
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"[Error: {type(error)} File:{filename} Line:{line}] Message: {str(error)}"
        ) 


async def catch_all_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        formatted_error = error_handler(exc)
        return JSONResponse(
            status_code=formatted_error.error_code.value,
            content={"error": formatted_error.message}
        )