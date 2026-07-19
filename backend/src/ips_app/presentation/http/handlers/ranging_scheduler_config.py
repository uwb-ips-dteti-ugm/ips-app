from typing import Optional

from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.ranging_scheduler_config import RangingSchedulerConfigUsecase
from ips_app.presentation.http.dto.ranging_scheduler_config import (
    RangingSchedulerConfigResponse,
    UpdateRangingSchedulerConfigRequest,
)


class RangingSchedulerConfigHandler:
    def __init__(self, usecase: RangingSchedulerConfigUsecase) -> None:
        self.usecase = usecase

    async def get_ranging_scheduler_config(self) -> RangingSchedulerConfigResponse:
        config = await self.usecase.get_config()
        return RangingSchedulerConfigResponse.from_domain(config)

    async def patch_ranging_scheduler_config(
        self,
        request: UpdateRangingSchedulerConfigRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> RangingSchedulerConfigResponse:
        config = await self.usecase.update_config(
            listen_timeout_uus=request.listen_timeout_uus,
            initiate_timeout_uus=request.initiate_timeout_uus,
            listen_to_initiate_delay_ms=request.listen_to_initiate_delay_ms,
            pair_delay_ms=request.pair_delay_ms,
            idle_delay_ms=request.idle_delay_ms,
            updated_by=claims.user_id if claims else None,
        )
        return RangingSchedulerConfigResponse.from_domain(config)

    async def post_ranging_scheduler_config_reset(
        self,
        claims: Optional[UserAccessTokenClaims],
    ) -> RangingSchedulerConfigResponse:
        config = await self.usecase.reset_config_to_default(
            updated_by=claims.user_id if claims else None,
        )
        return RangingSchedulerConfigResponse.from_domain(config)
