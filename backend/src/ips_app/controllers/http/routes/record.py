from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.controllers.http.dto.record import (
    LatestMultilaterationRecordRequest,
    LatestRangingRecordRequest,
    LatestRecordResponse,
    MultilaterationRecordIntervalRequest,
    RecordsResponse,
    RemovedRecordsResponse,
    RemoveMultilaterationRecordsByIntervalRequest,
    RemoveRangingRecordsByIntervalRequest,
    RangingRecordIntervalRequest,
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

    @router.get(
        "/ranging",
        response_model=RecordsResponse,
        dependencies=[
            logger(
                log,
                tag="RecordRoutes.get_ranging_records_by_interval",
                msg_2xx="Ranging records fetched by interval successfully",
                msg_4xx="Ranging records interval fetch rejected",
                msg_5xx="Ranging records interval fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_ranging_records_by_interval(
        start: datetime,
        end: datetime,
        source_node_device_ids: Optional[List[str]] = Query(None),
        target_node_device_ids: Optional[List[str]] = Query(None),
    ):
        request = RangingRecordIntervalRequest(
            start=start,
            end=end,
            source_node_device_ids=source_node_device_ids,
            target_node_device_ids=target_node_device_ids,
        )
        return await handler.get_ranging_records_by_interval(request)

    @router.get(
        "/ranging/latest",
        response_model=LatestRecordResponse,
        dependencies=[
            logger(
                log,
                tag="RecordRoutes.get_latest_ranging_record",
                msg_2xx="Latest ranging record fetched successfully",
                msg_4xx="Latest ranging record fetch rejected",
                msg_5xx="Latest ranging record fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_latest_ranging_record(
        source_node_device_ids: Optional[List[str]] = Query(None),
        target_node_device_ids: Optional[List[str]] = Query(None),
    ):
        request = LatestRangingRecordRequest(
            source_node_device_ids=source_node_device_ids,
            target_node_device_ids=target_node_device_ids,
        )
        return await handler.get_latest_ranging_record(request)

    @router.delete(
        "/ranging",
        response_model=RemovedRecordsResponse,
        dependencies=[
            logger(
                log,
                tag="RecordRoutes.delete_ranging_records_by_interval",
                msg_2xx="Ranging records deleted by interval successfully",
                msg_4xx="Ranging records interval deletion rejected",
                msg_5xx="Ranging records interval deletion failed",
            ),
            guard_delete,
        ],
    )
    async def delete_ranging_records_by_interval(
        request: RemoveRangingRecordsByIntervalRequest,
    ):
        return await handler.delete_ranging_records_by_interval(request)

    @router.get(
        "/multilateration",
        response_model=RecordsResponse,
        dependencies=[
            logger(
                log,
                tag="RecordRoutes.get_multilateration_records_by_interval",
                msg_2xx="Multilateration records fetched by interval successfully",
                msg_4xx="Multilateration records interval fetch rejected",
                msg_5xx="Multilateration records interval fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_multilateration_records_by_interval(
        start: datetime,
        end: datetime,
        ref_node_device_ids: Optional[List[str]] = Query(None),
        node_device_ids: Optional[List[str]] = Query(None),
    ):
        request = MultilaterationRecordIntervalRequest(
            start=start,
            end=end,
            ref_node_device_ids=ref_node_device_ids,
            node_device_ids=node_device_ids,
        )
        return await handler.get_multilateration_records_by_interval(request)

    @router.get(
        "/multilateration/latest",
        response_model=LatestRecordResponse,
        dependencies=[
            logger(
                log,
                tag="RecordRoutes.get_latest_multilateration_record",
                msg_2xx="Latest multilateration record fetched successfully",
                msg_4xx="Latest multilateration record fetch rejected",
                msg_5xx="Latest multilateration record fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_latest_multilateration_record(
        ref_node_device_ids: Optional[List[str]] = Query(None),
        node_device_ids: Optional[List[str]] = Query(None),
    ):
        request = LatestMultilaterationRecordRequest(
            ref_node_device_ids=ref_node_device_ids,
            node_device_ids=node_device_ids,
        )
        return await handler.get_latest_multilateration_record(request)

    @router.delete(
        "/multilateration",
        response_model=RemovedRecordsResponse,
        dependencies=[
            logger(
                log,
                tag="RecordRoutes.delete_multilateration_records_by_interval",
                msg_2xx="Multilateration records deleted by interval successfully",
                msg_4xx="Multilateration records interval deletion rejected",
                msg_5xx="Multilateration records interval deletion failed",
            ),
            guard_delete,
        ],
    )
    async def delete_multilateration_records_by_interval(
        request: RemoveMultilaterationRecordsByIntervalRequest,
    ):
        return await handler.delete_multilateration_records_by_interval(request)

    return router
