from abc import ABC, abstractmethod
from typing import Any, Optional

from ips_app.domain.models.ranging_scheduler_config import RangingSchedulerConfig


class RangingSchedulerConfigRepository(ABC):
    @abstractmethod
    async def load_cache(self, session: Optional[Any] = None) -> RangingSchedulerConfig: ...

    @abstractmethod
    async def get_cached_config(self) -> RangingSchedulerConfig: ...

    @abstractmethod
    async def update_config(
        self,
        listen_timeout_uus: Optional[int] = None,
        initiate_timeout_uus: Optional[int] = None,
        listen_to_initiate_delay_ms: Optional[int] = None,
        pair_delay_ms: Optional[int] = None,
        idle_delay_ms: Optional[int] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> RangingSchedulerConfig: ...

    @abstractmethod
    async def reset_config_to_default(
        self,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> RangingSchedulerConfig: ...
