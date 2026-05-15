from itertools import combinations
from typing import List, Optional, Sequence, Tuple

from ips_app.domain.models.exception import (
    DomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.node import Node
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.node.control import ControlNode
from ips_app.domain.ports.driven.repository.node import NodeRepository
from ips_app.domain.ports.driving.task.ranging_scheduler import RangingSchedulerTask
from ips_app.utils.validator import (
    validate_positive_integer,
    validate_required_uwb_network_value,
)


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
        self._registered_nodes: List[Node] = []
        self._node_pairs: List[Tuple[Node, Node]] = []
        self._node_pair_index = 0

    async def refresh_registered_nodes(self) -> None:
        tag = f"{self.tag_class}.refresh_registered_nodes"
        try:
            device_ids = await self.control.get_registered()
            nodes = await self._read_eligible_registered_nodes(device_ids)
            self._registered_nodes = nodes
            self._node_pairs = list(combinations(nodes, 2))
            self._node_pair_index = 0
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to refresh registered nodes",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_next_node_pair(self) -> Optional[Tuple[str, str, bool]]:
        tag = f"{self.tag_class}.get_next_node_pair"
        try:
            if not self._node_pairs:
                await self.refresh_registered_nodes()
            if not self._node_pairs:
                return None

            listener, initiator = self._node_pairs[self._node_pair_index]
            cycle_done = self._node_pair_index >= len(self._node_pairs) - 1
            if cycle_done:
                self._node_pair_index = 0
            else:
                self._node_pair_index += 1
                
            return listener.device_id, initiator.device_id, cycle_done
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get next node pair",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def listen_ranging(
        self,
        listener_device_id: str,
        initiator_device_id: str,
        listen_for_ms: int,
    ) -> None:
        tag = f"{self.tag_class}.listen_ranging"
        try:
            validate_positive_integer(
                listen_for_ms,
                "listen_for_ms",
            )
            listener = await self._ensure_approved_node(listener_device_id)
            initiator = await self._ensure_approved_node(initiator_device_id)
            listener_pan_id = validate_required_uwb_network_value(
                listener.pan_id,
                "listener_pan_id",
            )
            initiator_pan_id = validate_required_uwb_network_value(
                initiator.pan_id,
                "initiator_pan_id",
            )
            await self._ensure_registered_nodes(
                (listener_device_id, initiator_device_id)
            )
            await self.control.listen_ranging(
                device_id=listener_device_id,
                listener_pan_id=listener_pan_id,
                initiator_pan_id=initiator_pan_id,
                listen_for_ms=listen_for_ms,
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
                    "listener_pan_id": listener_pan_id,
                    "initiator_pan_id": initiator_pan_id,
                    "listen_for_ms": listen_for_ms,
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
        wait_for_ms: int,
    ) -> None:
        tag = f"{self.tag_class}.initiate_ranging"
        try:
            validate_positive_integer(
                wait_for_ms,
                "wait_for_ms",
            )
            initiator = await self._ensure_approved_node(initiator_device_id)
            target = await self._ensure_approved_node(target_device_id)
            initiator_pan_id = validate_required_uwb_network_value(
                initiator.pan_id,
                "initiator_pan_id",
            )
            listener_pan_id = validate_required_uwb_network_value(
                target.pan_id,
                "listener_pan_id",
            )
            await self._ensure_registered_nodes(
                (initiator_device_id, target_device_id)
            )
            await self.control.initiate_ranging(
                device_id=initiator_device_id,
                initiator_pan_id=initiator_pan_id,
                listener_pan_id=listener_pan_id,
                wait_for_ms=wait_for_ms,
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
                    "initiator_pan_id": initiator_pan_id,
                    "listener_pan_id": listener_pan_id,
                    "wait_for_ms": wait_for_ms,
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

    async def _read_eligible_registered_nodes(
        self,
        device_ids: Sequence[str],
    ) -> List[Node]:
        nodes: List[Node] = []
        for device_id in sorted(self._unique_device_ids(device_ids)):
            try:
                node = await self._ensure_approved_node(device_id)
                validate_required_uwb_network_value(node.pan_id, "pan_id")
                nodes.append(node)
            except NotFoundDomainException:
                continue
            except ForbiddenDomainException:
                continue
            except ValidatorDomainException:
                continue
        return nodes

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
