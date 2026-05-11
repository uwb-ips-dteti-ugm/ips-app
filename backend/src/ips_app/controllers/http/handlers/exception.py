from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    ExpiredTokenDomainException,
    ForbiddenDomainException,
    InvalidTokenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)


def handle_exception(
    error: Exception,
    domain_status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Internal server error"

    if isinstance(error, HTTPException):
        status_code = error.status_code
        message = str(error.detail)
    elif isinstance(error, ValidatorDomainException):
        status_code = status.HTTP_400_BAD_REQUEST
        message = str(error)
    elif isinstance(error, NotFoundDomainException):
        status_code = status.HTTP_404_NOT_FOUND
        message = f"Resource '{error.data_label}' in '{error.group_name}' not found"
    elif isinstance(error, DuplicateDomainException):
        status_code = status.HTTP_409_CONFLICT
        message = f"Resource '{error.data_label}' in '{error.group_name}' already exists"
    elif isinstance(error, ForbiddenDomainException):
        status_code = status.HTTP_403_FORBIDDEN
        message = str(error)
    elif isinstance(error, (ExpiredTokenDomainException, InvalidTokenDomainException)):
        status_code = status.HTTP_401_UNAUTHORIZED
        message = str(error)
    elif isinstance(error, UnexpectedDomainException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "Internal server error"
    elif isinstance(error, DomainException):
        status_code = domain_status_code
        message = str(error)

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=message).model_dump(),
    )
