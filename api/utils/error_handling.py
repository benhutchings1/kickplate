import random
import string
from os import path
from traceback import extract_stack

from fastapi import Request
from fastapi.responses import JSONResponse

from com_utils.backup_exception import BackupException
from com_utils.http import HttpCodes
from com_utils.logger import Loggers, LoggingLevel, api_logger


class CustomError(Exception):
    def __init__(
        self,
        error_code,
        logging_level: LoggingLevel,
        logger: Loggers = Loggers.GENERAL,
        message=None,
        logging_message=None,
    ) -> None:
        # Save inputs
        self.message = message
        self.error_code = error_code
        self.logging_message = logging_message
        self.logger = logger
        self.logging_level = logging_level

        # Check error code
        if isinstance(self.error_code, str):
            # Get error code from string
            self.error_code = HttpCodes[error_code]
        elif not isinstance(self.error_code, HttpCodes):
            # Get file and line of caller from stack trace
            filename, line = get_error_source(4)

            # Modify error to match
            self.error_code = HttpCodes.INTERNAL_SERVER_ERROR
            self.logging_message = f"File: {filename} Line: {line} tried to use non enumerated error code [{self.error_code}]"

        # Set error message if internal server error
        # but require internal logging message
        if self.message is None and self.error_code is HttpCodes.INTERNAL_SERVER_ERROR:
            if self.logging_message is None:
                filename, line = get_error_source(6)
                self.error_code = (HttpCodes.INTERNAL_SERVER_ERROR,)
                self.logging_message = f"File: {filename} Line: {line}\
                    raised internal server error without an logging message"
            # Report internal server error
            self.message = "Internal server error"
        elif self.message is None:
            raise CustomError(
                error_code=HttpCodes.INTERNAL_SERVER_ERROR,
                logging_message=f"raised error {error_code.name}\
                    without user message",
                message="Internal server error",
                logger=Loggers.GENERAL,
                logging_level=LoggingLevel.WARNING,
            )

        # if no logging message is given then revert to using main message
        if self.logging_message is None:
            self.logging_message = message

        # Insert error ID and error code
        error_log_message = f"[ERROR ID: {self.__generate_error_id()}]\
            [HTTP Code: {self.error_code.value}]\
                Message: {self.logging_message}"

        # Log messsage
        api_logger.log(
            logger=self.logger,
            logging_type=self.logging_level,
            message=error_log_message,
        )

    def __generate_error_id(self):
        # Use first 3 characters of logger name to prefix
        return self.logger.name[:3] + "".join(
            random.choices(string.ascii_uppercase + string.digits, k=5)
        )

    def __str__(self) -> str:
        return self.message


# Leave in error_handling to avoid circular import issues
def get_error_source(depth: int = 3) -> tuple[str, str]:
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
    """Handle general exceptions and reraise as CustomError"""
    if isinstance(error, CustomError):
        return error
    elif isinstance(error, BackupException):
        # convert BackupError to CustomError
        return CustomError(
            error_code=error.error_code,
            message=error.message,
            logging_level=error.logging_level,
            logger=error.logger,
            logging_message=error.logging_message,
        )
    else:
        # Catch unknown errors
        filename, line = get_error_source(4)
        # Raise soft error
        return CustomError(
            message="An unexpected error occured, please contact an admin",
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"[Error: {type(error)}\
                File:{filename} Line:{line}] Message: {str(error)}",
            logging_level=LoggingLevel.CRITICAL,
        )


async def catch_all_exceptions(request: Request, call_next):
    """Add top level exception handler"""
    try:
        return await call_next(request)
    except Exception as exc:
        formatted_error = error_handler(exc)
        return JSONResponse(
            status_code=formatted_error.error_code.value,
            content={"error": formatted_error.message},
        )
