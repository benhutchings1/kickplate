import os
from enum import Enum
import logging
from datetime import date
from src.backup_exception import BackupException

# Logging types
class LoggingLevel(Enum):
    '''Log markers'''
    # General error logs
    CRITICAL=logging.CRITICAL
    WARNING=logging.WARNING
    INFO=logging.INFO
    DEBUG=logging.DEBUG


class Loggers(Enum):
        '''Loggers and corresponding file'''
        SECURITY = "security.logs"
        ACCESS = "access.logs"
        GENERAL = "general.logs"
        USER_ERROR = "user_error.logs"

class __APILogger():    
    def __init__(self) -> None:
        # Define locations
        self.base_path = "./logs"
        
        # Manual override default logging message config
        # e.g. {Loggers.Security: "[Line: %(lineno)d] %(message)s"}
        self.format_override = {}
        self.default_format = "<%(levelname)s> [%(asctime)s]: %(message)s"
            
        # Setup logs
        self.__setup_logging_dirs()
        self.__make_files()
        
        # Make loggers
        self.__make_loggers()
        
            
    def __setup_logging_dirs(self):
        try:
            # Check for logging folder
            self.__make_dir(self.base_path)
            
            # Check for todays date logging folder
            self.log_path = f"{self.base_path}/logs_{date.today().strftime('%y-%m-%d')}"
            self.__make_dir(self.log_path)
            
            # Make files in folder
            self.__make_files()

        except PermissionError:
            # Print as logs cannot be used
            print("WARNING: COULD NOT CREATE LOGS (permission error)")
        except Exception as e:
            # Print as logs cannot be used
            print(f"WARNING: COULD NOT CREATE LOGS: Type {type(e)}: Message: {repr(e)}")

            
    def __make_dir(self, path) -> None:
        '''Create path if non existant'''
        if not os.path.exists(path):
            os.mkdir(path)
    
    
    def __make_files(self) -> None:
        '''make all log files from loggers in log path'''
        for filedef in Loggers:
            filepath = os.path.join(self.log_path, filedef.value)
            if not os.path.exists(filepath):
                # Make file if non existant
                with open(filepath, "w+"):
                    pass
    
    def __make_loggers(self) -> None:
        '''Uses enums to make loggers'''
        for enum in Loggers:
            form = self.default_format
            # Override default format
            if enum in self.format_override:
                form = self.format_override[enum]
            # Make logger with enum name as key
            logging.getLogger(enum.name)
            logging.basicConfig(
                filename=os.path.join(self.log_path, enum.value),
                level=logging.DEBUG,
                format=form
                )
           
    
    def __get_logger(self, logger) -> logging.Logger:
        '''Get logger given Logger enum or str equivilent'''
        if type(logger) is str: 
            # If type string, check if string version of enum exists
            if not logger in Loggers._member_names_:
                raise BackupException(
                    logging_message=f"Tried to get logger {logger} but didnt exist",
                )
            logger_name = logger
            
        elif issubclass(type(logger), Loggers):
            # Check if enum
            logger_name = logger.name
        else:
            # If not enum or str raise error
            raise BackupException(
                error_code="INTERNAL_SERVER_ERROR",
                logging_message=f"Tried to get logger {repr(logger)} which was type: {type(logger)}",
                # Raise as critical as logging is core aspect
                logging_level=LoggingLevel.CRITICAL
            )
        # Get logger given name
        try:
            return logging.getLogger(logger_name)
        except Exception as e:
            raise BackupException(
                error_code="INTERNAL_SERVER_ERROR",
                logging_message=f"Failed to get logger: error message {repr(e)}",
                # Raise as critical as logging is core aspect
                logging_level=LoggingLevel.CRITICAL                          
            )
    
    def log(self, logger:Loggers, message:str, logging_type:LoggingLevel) -> None:
        '''Write message to log, given logger and level'''
        # Param checks
        if not isinstance(logger, Loggers) \
            or logger is None:
                raise BackupException(
                    error_code="INTERNAL_SERVER_ERROR",
                    logging_message=f"Invalid logger type: {type(logger)} ",
                    logging_level=LoggingLevel.WARNING
                )
        if not isinstance(logging_type, LoggingLevel) \
            or logging_type is None:
                raise BackupException(
                    error_code="INTERNAL_SERVER_ERROR",
                    logging_message=f"Invalid logging type: {type(logging_type)}",
                    logging_level=LoggingLevel.WARNING
                )      
        
        # Get logger
        logger = self.__get_logger(logger)
        # Write to logs
        logging.log(level=logging_type.value, msg=message)
        
    
# SETUP LOGGER ON STARTUP
api_logger = __APILogger()

