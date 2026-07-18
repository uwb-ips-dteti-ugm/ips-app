class DomainException(Exception):
    """Base exception for all domain-related errors."""
    pass

class NotFoundDomainException(DomainException):
    def __init__(self, message: str = "Data is not found"):
        super().__init__(message)

class DuplicateDomainException(DomainException):
    def __init__(self, message: str = "Duplicate data"):
        super().__init__(message)

class ValidatorDomainException(DomainException):
    def __init__(self, message: str = "Invalid data"):
        super().__init__(message)

class ForbiddenDomainException(DomainException):
    def __init__(self, message: str = "Action is forbidden."):
        super().__init__(message)

class InvalidCredentialsDomainException(DomainException):
    def __init__(self, message: str = "Invalid credentials provided"):
        super().__init__(message)

class InvalidTokenDomainException(DomainException):
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)

class ExpiredTokenDomainException(DomainException):
    def __init__(self, message: str = "Expired token"):
        super().__init__(message)

class UnexpectedDomainException(DomainException):
    def __init__(self, message: str = "Unexpected error"):
        super().__init__(message)
