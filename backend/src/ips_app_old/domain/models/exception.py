class DomainException(Exception):
    """Base exception for all domain-related errors."""
    pass

class EnvRequiredDomainException(DomainException):
    def __init__(self, env_name: str):
        self.env_name = env_name
        super().__init__(f"Environment variable '{env_name}' is required.")

class NotFoundDomainException(DomainException):
    def __init__(self, data_label: str, group_name: str):
        self.data_label = data_label
        self.group_name = group_name
        super().__init__(f"'{data_label}' data in '{group_name}' is not found.")

class DuplicateDomainException(DomainException):
    def __init__(self, data_label: str, group_name: str):
        self.data_label = data_label
        self.group_name = group_name
        super().__init__(f"Duplicate '{data_label}' data in `{group_name}`")

class ValidatorDomainException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)

class ForbiddenDomainException(DomainException):
    def __init__(self, message: str = "Action is forbidden."):
        super().__init__(message)

class InvalidTokenDomainException(DomainException):
    def __init__(self):
        super().__init__("Token is invalid.")

class ExpiredTokenDomainException(DomainException):
    def __init__(self):
        super().__init__("Token has expired.")

class UnexpectedDomainException(DomainException):
    def __init__(self, error_msg: str):
        super().__init__(f"Unexpected error: {error_msg}")
