from typing import List, Optional, Sequence

from ips_app.domain.models.exception import (
    DomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.node import Node
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.node.control import ControlNode
from ips_app.domain.ports.driven.repository.node import NodeRepository
from ips_app.domain.ports.driving.task.ranging_scheduler import RangingSchedulerTask
from ips_app.utils.validator import validate_positive_integer


class BaseRangingSchedulerTask(RangingSchedulerTask):
    def __init__(
        self,
        repo_node: NodeRepository,
        control: ControlNode,
        log: GenericLogging,
    ):
        self.repo_node = repo_node
        self.control = control
        self.log = log
        self.tag_class = self.__class__.__name__

    async def get_registered_nodes(self) -> List[str]:
        tag = f"{self.tag_class}.get_registered_nodes"
        try:
            device_ids = await self.control.get_registered()
            await self.log.debug(
                tag,
                "Successfully fetched registered nodes",
                {"count": len(device_ids)},
            )
            return device_ids
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get registered nodes",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def listen_ranging(
        self,
        listener_device_id: str,
        initiator_device_id: str,
        listen_for: int,
    ) -> None:
        tag = f"{self.tag_class}.listen_ranging"
        try:
            validate_positive_integer(listen_for, "listen_for")
            await self._ensure_approved_nodes(
                (listener_device_id, initiator_device_id)
            )
            await self._ensure_registered_nodes(
                (listener_device_id, initiator_device_id)
            )
            await self.control.listen_ranging(
                listener_device_id=listener_device_id,
                initiator_device_id=initiator_device_id,
                listen_for=listen_for,
            )
            await self._set_nodes_last_seen(
                (listener_device_id, initiator_device_id)
            )
            await self.log.info(
                tag,
                "Successfully sent listen ranging command",
                {
                    "listener_device_id": listener_device_id,
                    "initiator_device_id": initiator_device_id,
                    "listen_for": listen_for,
                },
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to send listen ranging command",
                {
                    "error": str(e),
                    "listener_device_id": listener_device_id,
                    "initiator_device_id": initiator_device_id,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def initiate_ranging(
        self,
        initiator_device_id: str,
        target_device_id: str,
        wait_for: int,
    ) -> None:
        tag = f"{self.tag_class}.initiate_ranging"
        try:
            validate_positive_integer(wait_for, "wait_for")
            await self._ensure_approved_nodes(
                (initiator_device_id, target_device_id)
            )
            await self._ensure_registered_nodes(
                (initiator_device_id, target_device_id)
            )
            await self.control.initiate_ranging(
                initiator_device_id=initiator_device_id,
                target_device_id=target_device_id,
                wait_for=wait_for,
            )
            await self._set_nodes_last_seen(
                (initiator_device_id, target_device_id)
            )
            await self.log.info(
                tag,
                "Successfully sent initiate ranging command",
                {
                    "initiator_device_id": initiator_device_id,
                    "target_device_id": target_device_id,
                    "wait_for": wait_for,
                },
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to send initiate ranging command",
                {
                    "error": str(e),
                    "initiator_device_id": initiator_device_id,
                    "target_device_id": target_device_id,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def _ensure_approved_node(self, device_id: str) -> Node:
        node = await self.repo_node.read_node_by_device_id(device_id)
        if not node.is_approved:
            raise ForbiddenDomainException(f"Node '{device_id}' is not approved.")
        return node

    async def _ensure_approved_nodes(
        self,
        device_ids: Sequence[Optional[str]],
    ) -> None:
        for device_id in self._unique_device_ids(device_ids):
            await self._ensure_approved_node(device_id)

    async def _ensure_registered_nodes(self, device_ids: Sequence[str]) -> None:
        for device_id in self._unique_device_ids(device_ids):
            is_registered = await self.control.is_registered(device_id)
            if not is_registered:
                raise NotFoundDomainException(device_id, "node connections")

    async def _set_nodes_last_seen(
        self,
        device_ids: Sequence[Optional[str]],
    ) -> None:
        for device_id in self._unique_device_ids(device_ids):
            await self.repo_node.update_node_last_seen_at_by_device_id(device_id)

    def _unique_device_ids(
        self,
        device_ids: Sequence[Optional[str]],
    ) -> List[str]:
        unique_device_ids: List[str] = []
        seen_device_ids: set[str] = set()
        for device_id in device_ids:
            if device_id is None or device_id in seen_device_ids:
                continue

            unique_device_ids.append(device_id)
            seen_device_ids.add(device_id)

        return unique_device_ids
