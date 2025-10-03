from enum import Enum

class ErrorCode(Enum):
    """
    Enumeration of standardized error codes for the application.

    Each error code consists of a code string and a description.
    Example: E1001_GENERAL_ERROR = ("E1001", "A general unexpected error occurred.")
    """
    # General Errors (1xxx)
    E1001_GENERAL_ERROR = ("E1001", "A general unexpected error occurred.")
    E1002_CONFIGURATION_ERROR = ("E1002", "A configuration error occurred.")

    # File System Errors (2xxx)
    E2001_FILE_NOT_FOUND = ("E2001", "File or directory not found.")
    E2002_PERMISSION_DENIED = ("E2002", "Permission denied to access file or directory.")

    # Network Errors (3xxx)
    E3001_NETWORK_ERROR = ("E3001", "A network error occurred.")
    E3002_API_ERROR = ("E3002", "An API error occurred.")

    def __init__(self, code, description):
        self._code = code
        self._description = description

    @property
    def code(self):
        return self._code

    @property
    def description(self):
        return self._description

    def get_message(self, details=""):
        """Returns a formatted error message with optional details."""
        message = f"{self.code}: {self.description}"
        if details:
            message += f" Details: {details}"
        return message
