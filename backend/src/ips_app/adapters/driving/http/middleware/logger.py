import time
from fastapi import Depends, HTTPException, Request
from ips_app.ports.driven.logging.generic import GenericLoggingPort


def logger(
    log: GenericLoggingPort,
    tag: str = "LoggerHTTPMiddleware",
    msg_2xx: str = "Request successful",
    msg_4xx: str = "Client error",
    msg_5xx: str = "Server error",
):
    async def req_logger(request: Request):
        start = time.perf_counter()
        status_code = 200

        try:
            yield
        except HTTPException as exc:
            status_code = exc.status_code
            raise
        except Exception:
            status_code = 500
            raise
        finally:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            path = request.url.path
            query = request.url.query
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
                await log.error(tag, msg_5xx, meta)
            elif status_code >= 400:
                await log.warn(tag, msg_4xx, meta)
            else:
                await log.info(tag, msg_2xx, meta)

    return Depends(req_logger)
