import asyncio
from typing import Optional

from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driving.task.ranging_scheduler import (
    RangingSchedulerTask,
)


class RangingSchedulerTaskHandler:
    def __init__(
        self,
        service: RangingSchedulerTask,
        log: LeveledLogging,
    ):
        self.service = service
        self.log = log
        self.tag_class = self.__class__.__name__

    async def refresh_registered_nodes(self) -> None:
        tag = f"{self.tag_class}.refresh_registered_nodes"
        try:
            await self.service.refresh_registered_nodes()
        except DomainException as e:
            await self.log.error(
                tag,
                "Registered node refresh rejected",
                {"error": str(e)},
            )
        except Exception as e:
            error = UnexpectedDomainException(str(e))
            await self.log.error(
                tag,
                "Registered node refresh failed",
                {"error": str(error)},
            )

    async def run_next_ranging(
        self,
        listen_timeout_uus: int,
        initiate_timeout_uus: int,
        listen_to_initiate_delay_ms: int,
    ) -> Optional[bool]:
        tag = f"{self.tag_class}.run_next_ranging"
        try:
            pair = await self.service.get_next_node_pair()
            if pair is None:
                return None

            await self.service.listen_ranging(
                pair=pair,
                timeout_uus=listen_timeout_uus,
            )
            await asyncio.sleep(listen_to_initiate_delay_ms / 1000)
            await self.service.initiate_ranging(
                pair=pair,
                timeout_uus=initiate_timeout_uus,
            )
            return pair.cycle_done
        except DomainException as e:
            await self.log.error(
                tag,
                "Ranging schedule step rejected",
                {"error": str(e)},
            )
        except Exception as e:
            error = UnexpectedDomainException(str(e))
            await self.log.error(
                tag,
                "Ranging schedule step failed",
                {"error": str(error)},
            )
        return False
