from typing import Dict, Type

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    ExpiredTokenDomainException,
    ForbiddenDomainException,
    InvalidCredentialsDomainException,
    InvalidTokenDomainException,
    NodeNotConnectedDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.presentation.http.dto.common import ErrorResponse

EXCEPTION_STATUS_MAP: Dict[Type[Exception], int] = {
    ValidatorDomainException: 400,
    InvalidCredentialsDomainException: 401,
    InvalidTokenDomainException: 401,
    ExpiredTokenDomainException: 401,
    ForbiddenDomainException: 403,
    NotFoundDomainException: 404,
    DuplicateDomainException: 409,
    NodeNotConnectedDomainException: 409,
    UnexpectedDomainException: 500,
}


async def _handle_domain_exception(request: Request, exc: Exception) -> JSONResponse:
    status_code = EXCEPTION_STATUS_MAP.get(type(exc), 500)
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=str(exc)).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    for exception_cls in EXCEPTION_STATUS_MAP:
        app.add_exception_handler(exception_cls, _handle_domain_exception)
    app.add_exception_handler(DomainException, _handle_domain_exception)
