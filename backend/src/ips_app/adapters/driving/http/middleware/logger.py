import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from ips_app.ports.driven.logging.generic import GenericLoggingPort

class LoggerMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        log: GenericLoggingPort,
        msg_2xx: str = "Request successful",
        msg_4xx: str = "Client error",
        msg_5xx: str = "Server error",
    ):
        super().__init__(app)
        self.tag = "http/middleware/logger"
        self.log = log
        self.msg_2xx = msg_2xx
        self.msg_4xx = msg_4xx
        self.msg_5xx = msg_5xx

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        path = request.url.path
        query = request.url.query

        response = await call_next(request)

        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        status_code = response.status_code
        full_path = f"{path}?{query}" if query else path

        meta = {
            "status": status_code,
            "latency_ms": latency_ms,
            "client_ip": request.client.host if request.client else "unknown",
            "method": request.method,
            "path": full_path,
            "user_agent": request.headers.get("user-agent", ""),
        }

        if status_code >= 500:
            await self.log.error(self.tag, self.msg_5xx, meta)
        elif status_code >= 400:
            await self.log.warn(self.tag, self.msg_4xx, meta)
        else:
            await self.log.info(self.tag, self.msg_2xx, meta)

        return response
