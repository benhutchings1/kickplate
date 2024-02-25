from enum import Enum
from traceback import extract_stack
from os import path


class CustomError(Exception):
    def __init__(self, error_code, message=None, logging_message=None) -> None:        
        self.message = message
        super().__init__(message)
        
        # Check error code
        if not isinstance(error_code, HttpCodes):
            # Get file and line of caller from stack trace
            filename, line = get_error_source()
            # Raise error
            raise CustomError(
                error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                logging_message=f"File: {filename} Line: {line} tried to use non enumerated error code [{error_code}]"
            )
        self.error_code = error_code
        
        # Set error message if internal server error, but require internal logging message
        if self.message is None and error_code is HttpCodes.INTERNAL_SERVER_ERROR:
            if logging_message is None:
                raise CustomError(
                    error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                    logging_message=f"File: {filename} Line: {line} raised internal server error without an logging message"
                )
            self.message = "Internal server error"
        
        
        # if no logging message is given then revert to using main message
        if logging_message is None:
            self.logging_message = message
        
        # While logging not setup, print message
        print(logging_message)


class HttpCodes(Enum):
    OK=200
    CREATED=201
    ACCEPTED=202
    USER_ERROR=400
    USER_UNAUTHORISED=401
    NOT_FOUND=404
    CONFLICT=409
    INTERNAL_SERVER_ERROR=500
    TOO_LARGE=413
    TOO_MANY_REQUESTS=429


def get_error_source() -> tuple[str, str]:
    try:
        # Get file and line of caller from stack trace
        stack_item = list(extract_stack())[-3]
        __, filename = path.split(stack_item.filename)
        line = stack_item.lineno
    except IndexError:
        # Try again if there is no grandparent called 
        # Get file and line of caller from stack trace
        stack_item = list(extract_stack())[-2]
        __, filename = path.split(stack_item.filename)
        line = stack_item.lineno
    
    return (filename, line)