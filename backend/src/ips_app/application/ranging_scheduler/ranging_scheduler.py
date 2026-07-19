from itertools import combinations
from typing import Dict, List, Optional, Sequence

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.node.control import NodeControl
from ips_app.domain.contracts.repository.node import NodeRepository
from ips_app.domain.models.exception import (
    DomainException,
    NodeNotConnectedDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.domain.models.ranging import RangingPair
from ips_app.domain.usecases.ranging_scheduler import RangingSchedulerUsecase

from ips_app.application._shared.validator import validate_positive_integer


class BaseRangingSchedulerUsecase(RangingSchedulerUsecase):
    def __init__(self, repo: NodeRepository, control: NodeControl, log: LeveledLogger) -> None:
        self.repo = repo
        self.control = control
        self.log = log
        self.tag_class = self.__class__.__name__

        self._registered_nodes: List[Node] = []
        self._node_pairs: List[RangingPair] = []
        self._node_pair_index = 0

    async def refresh_registered_nodes(self) -> None:
        tag = f"{self.tag_class}/refresh_registered_nodes"
        try:
            device_ids = await self.control.get_registered()
            nodes = await self._read_eligible_registered_nodes(device_ids)
            self._registered_nodes = nodes
            self._node_pairs = self._build_node_pairs(nodes)
            self._node_pair_index = 0

            await self.log.info(
                tag,
                "Successfully refreshed registered nodes",
                {"node_count": len(nodes), "pair_count": len(self._node_pairs)},
            )
        except Exception as e:
            await self.log.error(
                tag, "Failed to refresh registered nodes", {"error": str(e)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_next_pair(self) -> Optional[RangingPair]:
        tag = f"{self.tag_class}/get_next_pair"
        try:
            await self._prune_unregistered_nodes()
            if not self._node_pairs:
                await self.refresh_registered_nodes()
                await self._prune_unregistered_nodes()

            if not self._node_pairs:
                return None

            pair = self._node_pairs[self._node_pair_index]
            cycle_done = self._node_pair_index >= len(self._node_pairs) - 1
            if cycle_done:
                self._node_pair_index = 0
            else:
                self._node_pair_index += 1

            return pair.model_copy(update={"cycle_done": cycle_done})
        except Exception as e:
            await self.log.error(tag, "Failed to get next ranging pair", {"error": str(e)})
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def listen(self, pair: RangingPair, timeout_uus: int) -> None:
        tag = f"{self.tag_class}/listen"
        try:
            validate_positive_integer(timeout_uus, "timeout_uus")
            device_ids = (pair.listener_node.device_id, pair.initiator_node.device_id)
            await self._ensure_registered_nodes(device_ids)

            await self.control.ranging_listen(
                device_id=pair.listener_node.device_id,
                pan_id=pair.network.pan_id,
                listener_address=self._require_address(pair.listener_node),
                initiator_address=self._require_address(pair.initiator_node),
                timeout_uus=timeout_uus,
            )
            await self._set_nodes_last_seen(device_ids)

            await self.log.debug(
                tag,
                "Successfully sent listen ranging command",
                {
                    "network_id": str(pair.network.id),
                    "pan_id": pair.network.pan_id,
                    "listener_device_id": pair.listener_node.device_id,
                    "initiator_device_id": pair.initiator_node.device_id,
                    "timeout_uus": timeout_uus,
                },
            )
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to send listen ranging command",
                {
                    "error": str(e),
                    "listener_device_id": pair.listener_node.device_id,
                    "initiator_device_id": pair.initiator_node.device_id,
                },
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def initiate(self, pair: RangingPair, timeout_uus: int) -> None:
        tag = f"{self.tag_class}/initiate"
        try:
            validate_positive_integer(timeout_uus, "timeout_uus")
            device_ids = (pair.listener_node.device_id, pair.initiator_node.device_id)
            await self._ensure_registered_nodes(device_ids)

            await self.control.ranging_initiate(
                device_id=pair.initiator_node.device_id,
                pan_id=pair.network.pan_id,
                initiator_address=self._require_address(pair.initiator_node),
                listener_address=self._require_address(pair.listener_node),
                timeout_uus=timeout_uus,
            )
            await self._set_nodes_last_seen(device_ids)

            await self.log.debug(
                tag,
                "Successfully sent initiate ranging command",
                {
                    "network_id": str(pair.network.id),
                    "pan_id": pair.network.pan_id,
                    "listener_device_id": pair.listener_node.device_id,
                    "initiator_device_id": pair.initiator_node.device_id,
                    "timeout_uus": timeout_uus,
                },
            )
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to send initiate ranging command",
                {
                    "error": str(e),
                    "listener_device_id": pair.listener_node.device_id,
                    "initiator_device_id": pair.initiator_node.device_id,
                },
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def _read_eligible_registered_nodes(self, device_ids: Sequence[str]) -> List[Node]:
        nodes: List[Node] = []
        for device_id in sorted(self._unique_device_ids(device_ids)):
            try:
                node = await self.repo.read_node_by_device_id(device_id)
            except NotFoundDomainException:
                continue
            if node.status != NodeStatus.APPROVED:
                continue
            if node.network is None or node.address is None:
                continue
            nodes.append(node)
        return nodes

    def _build_node_pairs(self, nodes: Sequence[Node]) -> List[RangingPair]:
        grouped_nodes: Dict[str, List[Node]] = {}
        for node in nodes:
            if node.network is None:
                continue
            grouped_nodes.setdefault(str(node.network.id), []).append(node)

        pairs: List[RangingPair] = []
        for network_id in sorted(grouped_nodes):
            network_nodes = sorted(grouped_nodes[network_id], key=lambda node: node.device_id)
            for listener, initiator in combinations(network_nodes, 2):
                if listener.network is None:
                    continue
                pairs.append(
                    RangingPair(
                        network=listener.network,
                        listener_node=listener,
                        initiator_node=initiator,
                        cycle_done=False,
                    )
                )
        return pairs

    async def _prune_unregistered_nodes(self) -> None:
        if not self._registered_nodes:
            return

        active_device_ids = set(await self.control.get_registered())
        missing_device_ids = [
            node.device_id
            for node in self._registered_nodes
            if node.device_id not in active_device_ids
        ]
        await self._set_nodes_last_disconnected(missing_device_ids)
        self._remove_nodes_from_schedule(missing_device_ids)

    def _remove_nodes_from_schedule(self, device_ids: Sequence[str]) -> None:
        removed_device_ids = set(self._unique_device_ids(device_ids))
        if not removed_device_ids:
            return

        self._registered_nodes = [
            node
            for node in self._registered_nodes
            if node.device_id not in removed_device_ids
        ]
        self._node_pairs = [
            pair
            for pair in self._node_pairs
            if (
                pair.listener_node.device_id not in removed_device_ids
                and pair.initiator_node.device_id not in removed_device_ids
            )
        ]
        if self._node_pairs:
            self._node_pair_index %= len(self._node_pairs)
        else:
            self._node_pair_index = 0

    async def _ensure_registered_nodes(self, device_ids: Sequence[str]) -> None:
        missing_device_ids: List[str] = []
        for device_id in self._unique_device_ids(device_ids):
            is_registered = await self.control.is_registered(device_id)
            if not is_registered:
                missing_device_ids.append(device_id)

        if missing_device_ids:
            await self._set_nodes_last_disconnected(missing_device_ids)
            self._remove_nodes_from_schedule(missing_device_ids)
            raise NodeNotConnectedDomainException(
                f"Node '{missing_device_ids[0]}' is not connected."
            )

    async def _set_nodes_last_seen(self, device_ids: Sequence[str]) -> None:
        for device_id in self._unique_device_ids(device_ids):
            await self.repo.update_node_last_seen_at_by_device_id(device_id)

    async def _set_nodes_last_disconnected(self, device_ids: Sequence[str]) -> None:
        for device_id in self._unique_device_ids(device_ids):
            try:
                await self.repo.update_node_last_disconnected_at_by_device_id(device_id)
            except DomainException:
                continue

    def _require_address(self, node: Node) -> int:
        if node.address is None:
            raise ValidatorDomainException(f"Node '{node.device_id}' must have an address.")
        return node.address

    def _unique_device_ids(self, device_ids: Sequence[str]) -> List[str]:
        unique_device_ids: List[str] = []
        seen_device_ids: set = set()
        for device_id in device_ids:
            if device_id in seen_device_ids:
                continue
            unique_device_ids.append(device_id)
            seen_device_ids.add(device_id)
        return unique_device_ids
