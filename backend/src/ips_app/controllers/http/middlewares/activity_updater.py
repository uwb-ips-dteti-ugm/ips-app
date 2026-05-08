from typing import Awaitable, Callable, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.ports.driving.http.user import UserHTTP


class ActivityUpdaterMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        user_service: UserHTTP,
        excluded_paths: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.user_service = user_service
        self.excluded_paths = set(excluded_paths or [])

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        response = await call_next(request)
        claims = get_claims()
        if not claims:
            return response

        try:
            await self.user_service.set_user_last_activity(claims.user_id)
        except Exception:
            pass

        return response
