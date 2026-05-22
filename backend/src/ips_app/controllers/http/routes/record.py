from fastapi import APIRouter

from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.controllers.http.dto.record import (
    RecordIntervalRequest,
    RecordsResponse,
    RemovedRecordsResponse,
    RemoveRecordsByIntervalRequest,
)
from ips_app.controllers.http.handlers.record import RecordHandler
from ips_app.controllers.http.middlewares.logger import logger
from ips_app.controllers.http.middlewares.permission_check import permission_check
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driving.http.role import RoleHTTP


def create_router(
    handler: RecordHandler,
    role_service: RoleHTTP,
    log: LeveledLogging,
) -> APIRouter:
    guard_view = permission_check(["record/view"], role_service)
    guard_delete = permission_check(["record/delete"], role_service)

    router = APIRouter(
        prefix="/records",
        tags=["Record"],
        responses={
            400: {"model": ErrorResponse, "description": "Bad Request"},
            401: {"model": ErrorResponse, "description": "Unauthorized"},
            403: {"model": ErrorResponse, "description": "Forbidden"},
            404: {"model": ErrorResponse, "description": "Not Found"},
            409: {"model": ErrorResponse, "description": "Conflict"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
        },
    )

    @router.post(
        "/query",
        response_model=RecordsResponse,
        dependencies=[
            logger(
                log,
                tag="RecordRoutes.get_records_by_interval",
                msg_2xx="Records fetched by interval successfully",
                msg_4xx="Records interval fetch rejected",
                msg_5xx="Records interval fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_records_by_interval(request: RecordIntervalRequest):
        return await handler.get_records_by_interval(request)

    @router.delete(
        "",
        response_model=RemovedRecordsResponse,
        dependencies=[
            logger(
                log,
                tag="RecordRoutes.delete_records_by_interval",
                msg_2xx="Records deleted by interval successfully",
                msg_4xx="Records interval deletion rejected",
                msg_5xx="Records interval deletion failed",
            ),
            guard_delete,
        ],
    )
    async def delete_records_by_interval(request: RemoveRecordsByIntervalRequest):
        return await handler.delete_records_by_interval(request)

    return router
