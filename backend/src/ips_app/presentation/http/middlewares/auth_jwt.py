from contextvars import ContextVar
from typing import List, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from ips_app.domain.contracts.utility.token import TokenIssuer
from ips_app.domain.models.exception import (
    ExpiredTokenDomainException,
    InvalidTokenDomainException,
)
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.presentation.http.dto.common import ErrorResponse

claims_context: ContextVar[Optional[UserAccessTokenClaims]] = ContextVar(
    "claims", default=None
)


class JwtMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        token_issuer: TokenIssuer,
        excluded_paths: Optional[List[str]] = None,
    ) -> None:
        super().__init__(app)
        self.token_issuer = token_issuer
        self.excluded_paths = set(excluded_paths or [])

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        token = self._extract_bearer_token(request)
        if not token:
            return self._unauthorized("Please sign in to continue.")

        try:
            claims = self.token_issuer.validate_access_token(token)
        except ExpiredTokenDomainException:
            return self._unauthorized("Your session has expired. Please sign in again.")
        except InvalidTokenDomainException:
            return self._unauthorized("Your session is invalid. Please sign in again.")
        except Exception:
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Something went wrong while verifying your session."
                ).model_dump(),
            )

        ctx_token = claims_context.set(claims)
        try:
            request.state.claims = claims
            return await call_next(request)
        finally:
            claims_context.reset(ctx_token)

    def _extract_bearer_token(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        return token

    def _unauthorized(self, error: str) -> JSONResponse:
        return JSONResponse(status_code=401, content=ErrorResponse(error=error).model_dump())


async def get_claims() -> Optional[UserAccessTokenClaims]:
    return claims_context.get()
