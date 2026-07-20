from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.ranging import (
    DeleteRangingRecordsResponse,
    RangingRecordResponse,
    ReportRangingMeasurementRequest,
)
from ips_app.presentation.http.handlers.ranging import RangingHandler
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import permission_check


def create_router(
    handler: RangingHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_manage = permission_check(["ranging/manage"], role_usecase)
    guard_view = permission_check(["ranging/view"], role_usecase)
    guard_delete = permission_check(["ranging/delete"], role_usecase)

    router = APIRouter(prefix="/ranging", tags=["Ranging"])

    @router.post(
        "/report",
        response_model=RangingRecordResponse,
        dependencies=[logger(log, "RangingRoutes/post_ranging_report"), guard_manage],
    )
    async def post_ranging_report(
        request: ReportRangingMeasurementRequest,
    ) -> RangingRecordResponse:
        return await handler.post_ranging_report(request)

    @router.get(
        "",
        response_model=List[RangingRecordResponse],
        dependencies=[
            logger(log, "RangingRoutes/get_ranging_records_by_interval"), guard_view
        ],
    )
    async def get_ranging_records_by_interval(
        start: datetime = Query(...),
        end: datetime = Query(...),
        network_id: Optional[str] = Query(None),
        node_id: Optional[str] = Query(None),
    ) -> List[RangingRecordResponse]:
        return await handler.get_ranging_records_by_interval(
            start, end, network_id, node_id
        )

    @router.get(
        "/latest",
        response_model=Optional[RangingRecordResponse],
        dependencies=[
            logger(log, "RangingRoutes/get_latest_ranging_record"), guard_view
        ],
    )
    async def get_latest_ranging_record(
        network_id: Optional[str] = Query(None),
        node_id: Optional[str] = Query(None),
    ) -> Optional[RangingRecordResponse]:
        return await handler.get_latest_ranging_record(network_id, node_id)

    @router.delete(
        "",
        response_model=DeleteRangingRecordsResponse,
        dependencies=[
            logger(log, "RangingRoutes/delete_ranging_records_by_interval"),
            guard_delete,
        ],
    )
    async def delete_ranging_records_by_interval(
        start: datetime = Query(...),
        end: datetime = Query(...),
        network_id: Optional[str] = Query(None),
        node_id: Optional[str] = Query(None),
    ) -> DeleteRangingRecordsResponse:
        return await handler.delete_ranging_records_by_interval(
            start, end, network_id, node_id
        )

    return router
