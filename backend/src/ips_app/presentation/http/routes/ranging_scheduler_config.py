from typing import Optional

from fastapi import APIRouter, Depends

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.ranging_scheduler_config import (
    RangingSchedulerConfigResponse,
    UpdateRangingSchedulerConfigRequest,
)
from ips_app.presentation.http.handlers.ranging_scheduler_config import (
    RangingSchedulerConfigHandler,
)
from ips_app.presentation.http.middlewares.auth_jwt import get_claims
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import permission_check


def create_router(
    handler: RangingSchedulerConfigHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_manage = permission_check(["ranging-scheduler-config/manage"], role_usecase)
    guard_view = permission_check(["ranging-scheduler-config/view"], role_usecase)

    router = APIRouter(prefix="/ranging-scheduler-config", tags=["RangingSchedulerConfig"])

    @router.get(
        "",
        response_model=RangingSchedulerConfigResponse,
        dependencies=[
            logger(log, "RangingSchedulerConfigRoutes/get_ranging_scheduler_config"),
            guard_view,
        ],
    )
    async def get_ranging_scheduler_config() -> RangingSchedulerConfigResponse:
        return await handler.get_ranging_scheduler_config()

    @router.patch(
        "",
        response_model=RangingSchedulerConfigResponse,
        dependencies=[
            logger(log, "RangingSchedulerConfigRoutes/patch_ranging_scheduler_config"),
            guard_manage,
        ],
    )
    async def patch_ranging_scheduler_config(
        request: UpdateRangingSchedulerConfigRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> RangingSchedulerConfigResponse:
        return await handler.patch_ranging_scheduler_config(request, claims)

    @router.post(
        "/reset",
        response_model=RangingSchedulerConfigResponse,
        dependencies=[
            logger(log, "RangingSchedulerConfigRoutes/post_ranging_scheduler_config_reset"),
            guard_manage,
        ],
    )
    async def post_ranging_scheduler_config_reset(
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> RangingSchedulerConfigResponse:
        return await handler.post_ranging_scheduler_config_reset(claims)

    return router
