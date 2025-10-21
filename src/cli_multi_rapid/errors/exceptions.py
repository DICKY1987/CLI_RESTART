from .error_codes import ErrorCode


class CLIOrchestratorException(Exception):
    """Base exception class for the CLI Orchestrator."""
    def __init__(self, error_code, details="", *args):
        self.error_code = error_code
        self.details = details
        super().__init__(self.error_code.get_message(details), *args)

class GeneralError(CLIOrchestratorException):
    """A general unexpected error."""
    def __init__(self, details="", *args):
        super().__init__(ErrorCode.E1001_GENERAL_ERROR, details, *args)

class ConfigurationError(CLIOrchestratorException):
    """A configuration error."""
    def __init__(self, details="", *args):
        super().__init__(ErrorCode.E1002_CONFIGURATION_ERROR, details, *args)

class FileNotFoundError(CLIOrchestratorException):
    """File or directory not found."""
    def __init__(self, details="", *args):
        super().__init__(ErrorCode.E2001_FILE_NOT_FOUND, details, *args)

class PermissionDeniedError(CLIOrchestratorException):
    """Permission denied to access file or directory."""
    def __init__(self, details="", *args):
        super().__init__(ErrorCode.E2002_PERMISSION_DENIED, details, *args)

class NetworkError(CLIOrchestratorException):
    """A network error occurred."""
    def __init__(self, details="", *args):
        super().__init__(ErrorCode.E3001_NETWORK_ERROR, details, *args)

class APIError(CLIOrchestratorException):
    """An API error occurred."""
    def __init__(self, details="", *args):
        super().__init__(ErrorCode.E3002_API_ERROR, details, *args)
