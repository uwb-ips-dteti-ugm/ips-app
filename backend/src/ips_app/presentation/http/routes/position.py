from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.position import (
    ComputeTagPositionRequest,
    PositionRecordResponse,
)
from ips_app.presentation.http.handlers.position import PositionHandler
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import permission_check


def create_router(
    handler: PositionHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_view = permission_check(["node/view", "ranging/view"], role_usecase)

    router = APIRouter(prefix="/position", tags=["Position"])

    @router.post(
        "/compute",
        response_model=Optional[PositionRecordResponse],
        dependencies=[
            logger(log, "PositionRoutes/post_position_compute"), guard_view
        ],
    )
    async def post_position_compute(
        request: ComputeTagPositionRequest,
    ) -> Optional[PositionRecordResponse]:
        return await handler.post_position_compute(request)

    @router.get(
        "",
        response_model=List[PositionRecordResponse],
        dependencies=[
            logger(log, "PositionRoutes/get_position_records_by_interval"), guard_view
        ],
    )
    async def get_position_records_by_interval(
        start: datetime = Query(...),
        end: datetime = Query(...),
        network_id: Optional[str] = Query(None),
        tag_node_id: Optional[str] = Query(None),
    ) -> List[PositionRecordResponse]:
        return await handler.get_position_records_by_interval(
            start, end, network_id, tag_node_id
        )

    @router.get(
        "/latest",
        response_model=Optional[PositionRecordResponse],
        dependencies=[
            logger(log, "PositionRoutes/get_latest_position_record"), guard_view
        ],
    )
    async def get_latest_position_record(
        network_id: Optional[str] = Query(None),
        tag_node_id: Optional[str] = Query(None),
    ) -> Optional[PositionRecordResponse]:
        return await handler.get_latest_position_record(network_id, tag_node_id)

    return router
