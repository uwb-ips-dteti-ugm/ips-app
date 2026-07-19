from typing import Any, Optional

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.repository.ranging_scheduler_config import (
    RangingSchedulerConfigRepository,
)
from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.ranging_scheduler_config import RangingSchedulerConfig
from ips_app.domain.usecases.ranging_scheduler_config import RangingSchedulerConfigUsecase

from ips_app.application._shared.validator import validate_positive_integer


class BaseRangingSchedulerConfigUsecase(RangingSchedulerConfigUsecase):
    def __init__(self, repo: RangingSchedulerConfigRepository, log: LeveledLogger) -> None:
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def get_config(self) -> RangingSchedulerConfig:
        tag = f"{self.tag_class}/get_config"
        try:
            return await self.repo.get_cached_config()
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve ranging scheduler config", {"error": str(e)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_config(
        self,
        listen_timeout_uus: Optional[int] = None,
        initiate_timeout_uus: Optional[int] = None,
        listen_to_initiate_delay_ms: Optional[int] = None,
        pair_delay_ms: Optional[int] = None,
        idle_delay_ms: Optional[int] = None,
        updated_by: Optional[Any] = None,
    ) -> RangingSchedulerConfig:
        tag = f"{self.tag_class}/update_config"
        try:
            for value, field in (
                (listen_timeout_uus, "listen_timeout_uus"),
                (initiate_timeout_uus, "initiate_timeout_uus"),
                (listen_to_initiate_delay_ms, "listen_to_initiate_delay_ms"),
                (pair_delay_ms, "pair_delay_ms"),
                (idle_delay_ms, "idle_delay_ms"),
            ):
                if value is not None:
                    validate_positive_integer(value, field)
            config = await self.repo.update_config(
                listen_timeout_uus=listen_timeout_uus,
                initiate_timeout_uus=initiate_timeout_uus,
                listen_to_initiate_delay_ms=listen_to_initiate_delay_ms,
                pair_delay_ms=pair_delay_ms,
                idle_delay_ms=idle_delay_ms,
                updated_by=updated_by,
            )
            await self.log.info(tag, "Successfully updated ranging scheduler config", {})
            return config
        except Exception as e:
            await self.log.error(
                tag, "Failed to update ranging scheduler config", {"error": str(e)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def reset_config_to_default(
        self,
        updated_by: Optional[Any] = None,
    ) -> RangingSchedulerConfig:
        tag = f"{self.tag_class}/reset_config_to_default"
        try:
            config = await self.repo.reset_config_to_default(updated_by=updated_by)
            await self.log.info(
                tag, "Successfully reset ranging scheduler config to default", {}
            )
            return config
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to reset ranging scheduler config to default",
                {"error": str(e)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e
