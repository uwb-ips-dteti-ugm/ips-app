from contextvars import ContextVar
from typing import Awaitable, Callable, List, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.domain.models.exception import (
    ExpiredTokenDomainException,
    InvalidTokenDomainException,
)
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.utils.token import validate_access_token


claims_context: ContextVar[Optional[UserAccessTokenClaims]] = ContextVar(
    "claims",
    default=None,
)


class JwtMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        excluded_paths: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.excluded_paths = set(excluded_paths or [])

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        token = self._extract_bearer_token(request)
        if not token:
            return self._unauthorized("Please sign in to continue.")

        try:
            claims = validate_access_token(token)
        except ExpiredTokenDomainException:
            return self._unauthorized("Your session has expired. Please sign in again.")
        except InvalidTokenDomainException:
            return self._unauthorized("Your session is invalid. Please sign in again.")
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while checking your session. Please try again."
                ).model_dump(),
            )

        ctx_token = claims_context.set(claims)
        try:
            request.state.claims = claims
            return await call_next(request)
        finally:
            claims_context.reset(ctx_token)

    def _extract_bearer_token(self, request: Request) -> str:
        authorization = request.headers.get("Authorization", "")
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return ""
        return parts[1]

    def _unauthorized(self, error: str) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(error=error).model_dump(),
        )


def get_claims() -> Optional[UserAccessTokenClaims]:
    return claims_context.get()
