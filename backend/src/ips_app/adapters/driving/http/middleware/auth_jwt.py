from typing import List, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from ips_app.adapters.driving.http.dto.common import ErrorResponse
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.models.exception import InvalidTokenException, ExpiredTokenException
from ips_app.utils.token import validate_access_token

class JwtMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        excluded_paths: List[str] = [],
    ):
        super().__init__(app)
        self.excluded_paths = excluded_paths

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        token = await self._extract_bearer_token(request)
        if not token:
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(error="Valid bearer authorization header is required").model_dump(),
            )

        try:
            claims = validate_access_token(token)
        except ExpiredTokenException:
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(error="Expired access token").model_dump(),
            )
        except InvalidTokenException:
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(error="Invalid access token").model_dump(),
            )

        request.state.claims = claims
        return await call_next(request)
        
    async def _extract_bearer_token(self, request: Request) -> str:
        authorization = request.headers.get("Authorization", "")
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            return ""
        return parts[1]


def get_claims(request: Request) -> Optional[UserAccessTokenClaims]:
    return getattr(request.state, "claims", None)
