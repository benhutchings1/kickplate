class BackupException(Exception):
    """
    Backup exception as Logging cannot import CustomError \
        due to circular import
    Will be reraised as a CustomError
    """

    def __init__(
        self, error_code, logging_level, logger, message=None, logging_message=None
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.logging_message = logging_message
        self.logger = logger
        self.logging_level = logging_level
