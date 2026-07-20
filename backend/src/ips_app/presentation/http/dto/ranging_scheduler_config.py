from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.ranging_scheduler_config import RangingSchedulerConfig
from ips_app.presentation.http.dto.common import AuditedResponse, stringify_id


class UpdateRangingSchedulerConfigRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    listen_timeout_uus: Optional[int] = Field(None, gt=0)
    initiate_timeout_uus: Optional[int] = Field(None, gt=0)
    listen_to_initiate_delay_ms: Optional[int] = Field(None, gt=0)
    pair_delay_ms: Optional[int] = Field(None, gt=0)
    idle_delay_ms: Optional[int] = Field(None, gt=0)


class RangingSchedulerConfigResponse(AuditedResponse):
    id: str
    listen_timeout_uus: int
    initiate_timeout_uus: int
    listen_to_initiate_delay_ms: int
    pair_delay_ms: int
    idle_delay_ms: int

    @classmethod
    def from_domain(cls, config: RangingSchedulerConfig) -> "RangingSchedulerConfigResponse":
        return cls(
            id=str(config.id),
            listen_timeout_uus=config.listen_timeout_uus,
            initiate_timeout_uus=config.initiate_timeout_uus,
            listen_to_initiate_delay_ms=config.listen_to_initiate_delay_ms,
            pair_delay_ms=config.pair_delay_ms,
            idle_delay_ms=config.idle_delay_ms,
            created_at=config.created_at,
            created_by=stringify_id(config.created_by),
            updated_at=config.updated_at,
            updated_by=stringify_id(config.updated_by),
        )
