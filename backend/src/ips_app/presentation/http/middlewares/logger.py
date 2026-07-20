import time
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.exception import DomainException
from ips_app.presentation.http.exception import EXCEPTION_STATUS_MAP


def logger(log: LeveledLogger, tag: str):
    async def req_logger(request: Request) -> AsyncGenerator[None, None]:
        start = time.perf_counter()
        status_code = 200
        try:
            yield
        except HTTPException as e:
            status_code = e.status_code
            raise
        except DomainException as e:
            status_code = EXCEPTION_STATUS_MAP.get(type(e), 500)
            raise
        except Exception:
            status_code = 500
            raise
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            meta = {
                "status": status_code,
                "latency_ms": round(latency_ms, 2),
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
            if status_code >= 500:
                await log.error(tag, "Request failed", meta)
            elif status_code >= 400:
                await log.warn(tag, "Request rejected", meta)
            else:
                await log.info(tag, "Request completed", meta)

    return Depends(req_logger)
