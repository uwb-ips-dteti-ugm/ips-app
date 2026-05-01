class DomainException(Exception):
    """Base exception for all domain-related errors."""
    pass

class EnvRequiredException(DomainException):
    def __init__(self, env_name: str):
        self.env_name = env_name
        super().__init__(f"Environment variable '{env_name}' is required.")

class NotFoundException(DomainException):
    def __init__(self, data_name: str, group_name: str):
        self.data_name = data_name
        self.group_name = group_name
        super().__init__(f"'{data_name}' data in '{group_name}' is not found.")

class DuplicateException(DomainException):
    def __init__(self, data_name: str, group_name: str):
        self.data_name = data_name
        self.group_name = group_name
        super().__init__(f"Duplicate '{data_name}' data in `{group_name}`")

class InternalServerException(DomainException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message)
