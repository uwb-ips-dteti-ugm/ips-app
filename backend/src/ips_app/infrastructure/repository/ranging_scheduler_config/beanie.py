import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ips_app.domain.contracts.repository.ranging_scheduler_config import (
    RangingSchedulerConfigRepository,
)
from ips_app.domain.models.exception import DomainException, NotFoundDomainException, UnexpectedDomainException
from ips_app.domain.models.ranging_scheduler_config import RangingSchedulerConfig
from ips_app.infrastructure.repository.ranging_scheduler_config.beanie_model import (
    RangingSchedulerConfigDocument,
)


class BeanieRangingSchedulerConfigRepository(RangingSchedulerConfigRepository):
    def __init__(self, defaults: RangingSchedulerConfig) -> None:
        self.defaults = defaults
        self._cache: Optional[RangingSchedulerConfig] = None
        self.lock = asyncio.Lock()

    async def load_cache(self, session: Optional[Any] = None) -> RangingSchedulerConfig:
        try:
            async with self.lock:
                doc = await RangingSchedulerConfigDocument.find_one({}, session=session)
                if doc is None:
                    doc = RangingSchedulerConfigDocument(
                        listen_timeout_uus=self.defaults.listen_timeout_uus,
                        initiate_timeout_uus=self.defaults.initiate_timeout_uus,
                        listen_to_initiate_delay_ms=self.defaults.listen_to_initiate_delay_ms,
                        pair_delay_ms=self.defaults.pair_delay_ms,
                        idle_delay_ms=self.defaults.idle_delay_ms,
                    )
                    await doc.insert(session=session)
                self._cache = doc.to_domain()
                return self._cache
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def get_cached_config(self) -> RangingSchedulerConfig:
        async with self.lock:
            if self._cache is None:
                raise UnexpectedDomainException(
                    "Ranging scheduler config cache has not been loaded."
                )
            return self._cache

    async def update_config(
        self,
        listen_timeout_uus: Optional[int] = None,
        initiate_timeout_uus: Optional[int] = None,
        listen_to_initiate_delay_ms: Optional[int] = None,
        pair_delay_ms: Optional[int] = None,
        idle_delay_ms: Optional[int] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> RangingSchedulerConfig:
        try:
            async with self.lock:
                doc = await RangingSchedulerConfigDocument.find_one({}, session=session)
                if doc is None:
                    raise NotFoundDomainException("Ranging scheduler config not found")

                update_data: Dict[str, Any] = {
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
                }
                if listen_timeout_uus is not None:
                    update_data["listen_timeout_uus"] = listen_timeout_uus
                if initiate_timeout_uus is not None:
                    update_data["initiate_timeout_uus"] = initiate_timeout_uus
                if listen_to_initiate_delay_ms is not None:
                    update_data["listen_to_initiate_delay_ms"] = listen_to_initiate_delay_ms
                if pair_delay_ms is not None:
                    update_data["pair_delay_ms"] = pair_delay_ms
                if idle_delay_ms is not None:
                    update_data["idle_delay_ms"] = idle_delay_ms

                await doc.set(update_data, session=session)
                self._cache = doc.to_domain()
                return self._cache
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def reset_config_to_default(
        self,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> RangingSchedulerConfig:
        return await self.update_config(
            listen_timeout_uus=self.defaults.listen_timeout_uus,
            initiate_timeout_uus=self.defaults.initiate_timeout_uus,
            listen_to_initiate_delay_ms=self.defaults.listen_to_initiate_delay_ms,
            pair_delay_ms=self.defaults.pair_delay_ms,
            idle_delay_ms=self.defaults.idle_delay_ms,
            updated_by=updated_by,
            session=session,
        )
