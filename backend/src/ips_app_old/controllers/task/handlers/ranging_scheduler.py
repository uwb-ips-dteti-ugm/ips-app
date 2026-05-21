from typing import Optional

from ips_app_old.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app_old.domain.ports.driven.logging.generic import GenericLogging
from ips_app_old.domain.ports.driving.task.ranging_scheduler import RangingSchedulerTask


class RangingSchedulerTaskHandler:
    def __init__(
        self,
        service: RangingSchedulerTask,
        log: GenericLogging,
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
        listen_for_ms: int,
        wait_for_ms: int,
    ) -> Optional[bool]:
        tag = f"{self.tag_class}.run_next_ranging"
        try:
            node_pair = await self.service.get_next_node_pair()
            if node_pair is None:
                return None

            listener_device_id, initiator_device_id, cycle_done = node_pair
            await self.service.listen_ranging(
                listener_device_id=listener_device_id,
                initiator_device_id=initiator_device_id,
                listen_for_ms=listen_for_ms,
            )
            await self.service.initiate_ranging(
                initiator_device_id=initiator_device_id,
                target_device_id=listener_device_id,
                wait_for_ms=wait_for_ms,
            )
            return cycle_done
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
