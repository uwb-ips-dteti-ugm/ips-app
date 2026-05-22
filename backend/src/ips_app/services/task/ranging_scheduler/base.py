from itertools import combinations
from typing import Dict, List, Optional, Sequence

from ips_app.domain.models.exception import (
    DomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.node import Node
from ips_app.domain.models.ranging import RangingNodePair
from ips_app.domain.ports.driven.control.node import NodeControl
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.node import NodeRepository
from ips_app.domain.ports.driving.task.ranging_scheduler import (
    RangingSchedulerTask,
)


class BaseRangingSchedulerTask(RangingSchedulerTask):
    def __init__(
        self,
        repo_node: NodeRepository,
        control: NodeControl,
        log: LeveledLogging,
    ):
        self.repo_node = repo_node
        self.control = control
        self.log = log
        self.tag_class = self.__class__.__name__
        self._registered_nodes: List[Node] = []
        self._node_pairs: List[RangingNodePair] = []
        self._node_pair_index = 0

    async def refresh_registered_nodes(self) -> None:
        tag = f"{self.tag_class}.refresh_registered_nodes"
        try:
            device_ids = await self.control.get_registered()
            nodes = await self._read_eligible_registered_nodes(device_ids)
            self._registered_nodes = nodes
            self._node_pairs = self._build_node_pairs(nodes)
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

    async def get_next_node_pair(self) -> Optional[RangingNodePair]:
        tag = f"{self.tag_class}.get_next_node_pair"
        try:
            if not self._node_pairs:
                await self.refresh_registered_nodes()
            if not self._node_pairs:
                return None

            pair = self._node_pairs[self._node_pair_index]
            cycle_done = self._node_pair_index >= len(self._node_pairs) - 1
            if cycle_done:
                self._node_pair_index = 0
            else:
                self._node_pair_index += 1

            return pair.model_copy(update={"cycle_done": cycle_done})
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
        pair: RangingNodePair,
        timeout_uus: int,
    ) -> None:
        tag = f"{self.tag_class}.listen_ranging"
        try:
            self._validate_positive_integer(timeout_uus, "timeout_uus")
            await self._ensure_registered_nodes(
                (pair.listener_device_id, pair.initiator_device_id)
            )
            await self.control.listen_ranging(
                device_id=pair.listener_device_id,
                pan_id=pair.pan_id,
                listener_address=pair.listener_address,
                initiator_address=pair.initiator_address,
                timeout_uus=timeout_uus,
            )
            await self._set_nodes_last_seen(
                (pair.listener_device_id, pair.initiator_device_id)
            )
            await self.log.debug(
                tag,
                "Successfully sent listen ranging command",
                {
                    "network_id": str(pair.network_id),
                    "pan_id": pair.pan_id,
                    "listener_device_id": pair.listener_device_id,
                    "initiator_device_id": pair.initiator_device_id,
                    "timeout_uus": timeout_uus,
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
                    "listener_device_id": pair.listener_device_id,
                    "initiator_device_id": pair.initiator_device_id,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def initiate_ranging(
        self,
        pair: RangingNodePair,
        timeout_uus: int,
    ) -> None:
        tag = f"{self.tag_class}.initiate_ranging"
        try:
            self._validate_positive_integer(timeout_uus, "timeout_uus")
            await self._ensure_registered_nodes(
                (pair.listener_device_id, pair.initiator_device_id)
            )
            await self.control.initiate_ranging(
                device_id=pair.initiator_device_id,
                pan_id=pair.pan_id,
                initiator_address=pair.initiator_address,
                listener_address=pair.listener_address,
                timeout_uus=timeout_uus,
            )
            await self._set_nodes_last_seen(
                (pair.listener_device_id, pair.initiator_device_id)
            )
            await self.log.debug(
                tag,
                "Successfully sent initiate ranging command",
                {
                    "network_id": str(pair.network_id),
                    "pan_id": pair.pan_id,
                    "listener_device_id": pair.listener_device_id,
                    "initiator_device_id": pair.initiator_device_id,
                    "timeout_uus": timeout_uus,
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
                    "listener_device_id": pair.listener_device_id,
                    "initiator_device_id": pair.initiator_device_id,
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
                self._ensure_node_has_network_assignment(node)
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
        device_ids: Sequence[str],
    ) -> None:
        for device_id in self._unique_device_ids(device_ids):
            await self.repo_node.update_node_last_seen_at_by_device_id(device_id)

    def _build_node_pairs(self, nodes: Sequence[Node]) -> List[RangingNodePair]:
        grouped_nodes: Dict[str, List[Node]] = {}
        for node in nodes:
            network_id = str(self._node_network_id(node))
            grouped_nodes.setdefault(network_id, []).append(node)

        pairs: List[RangingNodePair] = []
        for network_id in sorted(grouped_nodes):
            network_nodes = sorted(
                grouped_nodes[network_id],
                key=lambda node: node.device_id,
            )
            for listener, initiator in combinations(network_nodes, 2):
                pairs.append(self._create_node_pair(listener, initiator))

        return pairs

    def _create_node_pair(self, listener: Node, initiator: Node) -> RangingNodePair:
        listener_network_id = self._node_network_id(listener)
        initiator_network_id = self._node_network_id(initiator)
        if str(listener_network_id) != str(initiator_network_id):
            raise ValidatorDomainException(
                "Ranging node pairs must belong to the same network."
            )
        if listener.network is None:
            raise ValidatorDomainException("Listener node must have a network.")
        if listener.address is None or initiator.address is None:
            raise ValidatorDomainException("Ranging nodes must have addresses.")

        return RangingNodePair(
            network_id=listener_network_id,
            pan_id=listener.network.pan_id,
            listener_device_id=listener.device_id,
            listener_address=listener.address,
            initiator_device_id=initiator.device_id,
            initiator_address=initiator.address,
            cycle_done=False,
        )

    def _ensure_node_has_network_assignment(self, node: Node) -> None:
        self._node_network_id(node)
        if node.network is None:
            raise ValidatorDomainException("Node must have a network.")
        if node.address is None:
            raise ValidatorDomainException("Node must have an address.")

    def _node_network_id(self, node: Node) -> object:
        if node.network is None or node.network.id is None:
            raise ValidatorDomainException("Node must have a network ID.")
        return node.network.id

    def _unique_device_ids(self, device_ids: Sequence[str]) -> List[str]:
        unique_device_ids: List[str] = []
        seen_device_ids: set[str] = set()
        for device_id in device_ids:
            if device_id in seen_device_ids:
                continue

            unique_device_ids.append(device_id)
            seen_device_ids.add(device_id)

        return unique_device_ids

    def _validate_positive_integer(self, value: int, field: str) -> None:
        if value <= 0:
            raise ValidatorDomainException(f"{field} must be greater than 0.")
