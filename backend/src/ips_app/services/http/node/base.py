from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.domain.models.record import RecordDataLabel, RecordDataRanging
from ips_app.domain.ports.driven.control.node import NodeControl
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.node import NodeRepository
from ips_app.domain.ports.driven.repository.node_network import (
    NodeNetworkRepository,
)
from ips_app.domain.ports.driven.repository.record import RecordRepository
from ips_app.domain.ports.driving.http.node import NodeHTTP
from ips_app.utils.namegen import generate_name
from ips_app.utils.validator import (
    validate_non_empty_string,
    validate_non_negative_float,
    validate_uwb_value,
)


class BaseNodeHTTP(NodeHTTP):
    def __init__(
        self,
        repo: NodeRepository,
        repo_node_network: NodeNetworkRepository,
        repo_record: RecordRepository,
        control: NodeControl,
        log: LeveledLogging,
    ):
        self.repo = repo
        self.repo_node_network = repo_node_network
        self.repo_record = repo_record
        self.control = control
        self.log = log
        self.tag_class = self.__class__.__name__

    async def add_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        created_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}.add_node"
        try:
            node = await self.repo.create_node(
                device_id=device_id,
                name=name,
                description=description,
                network_id=network_id,
                address=address,
                preferences=preferences,
                created_by=created_by,
            )
            await self.log.info(
                tag,
                "Successfully added node",
                {"id": str(node.id), "device_id": device_id},
            )
            return node
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add node",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_node(self, node_id: Any) -> Node:
        tag = f"{self.tag_class}.get_node"
        try:
            return await self.repo.read_node_by_id(node_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get node",
                {"error": str(e), "id": str(node_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_by_device_id(self, device_id: str) -> Node:
        tag = f"{self.tag_class}.get_node_by_device_id"
        try:
            return await self.repo.read_node_by_device_id(device_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get node by device id",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_by_network_address(
        self,
        network_id: Any,
        address: int,
    ) -> Node:
        tag = f"{self.tag_class}.get_node_by_network_address"
        try:
            return await self.repo.read_node_by_network_id_and_address(
                network_id=network_id,
                address=address,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get node by network address",
                {
                    "error": str(e),
                    "network_id": str(network_id),
                    "address": address,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_nodes(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
    ) -> Tuple[List[Node], int]:
        tag = f"{self.tag_class}.get_nodes"
        try:
            return await self.repo.read_nodes_by_pagination(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
                status=status,
                network_id=network_id,
                address=address,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get nodes",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_node_info(
        self,
        node_id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}.set_node_info"
        try:
            await self.repo.update_node_info_by_id(
                id=node_id,
                name=name,
                description=description,
                updated_by=updated_by,
            )
            node = await self.get_node(node_id)
            await self.log.info(
                tag,
                "Successfully updated node info",
                {"id": str(node_id)},
            )
            return node
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set node info",
                {"error": str(e), "id": str(node_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_node_network_assignment(
        self,
        node_id: Any,
        network_id: Optional[Any],
        address: Optional[int],
        updated_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}.set_node_network_assignment"
        try:
            await self.repo.update_node_network_assignment_by_id(
                id=node_id,
                network_id=network_id,
                address=address,
                updated_by=updated_by,
            )
            node = await self.get_node(node_id)
            await self.log.info(
                tag,
                "Successfully updated node network assignment",
                {"id": str(node_id), "network_id": str(network_id)},
            )
            return node
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set node network assignment",
                {"error": str(e), "id": str(node_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_node_status(
        self,
        node_id: Any,
        status: NodeStatus,
        updated_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}.set_node_status"
        try:
            await self.repo.update_node_status_by_id(
                id=node_id,
                status=status,
                updated_by=updated_by,
            )
            node = await self.get_node(node_id)
            await self.log.info(
                tag,
                "Successfully updated node status",
                {"id": str(node_id), "status": str(status)},
            )
            return node
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set node status",
                {"error": str(e), "id": str(node_id), "status": str(status)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_node_preferences(
        self,
        node_id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}.set_node_preferences"
        try:
            await self.repo.update_node_preferences_by_id(
                id=node_id,
                preferences=preferences,
                updated_by=updated_by,
            )
            node = await self.get_node(node_id)
            await self.log.info(
                tag,
                "Successfully updated node preferences",
                {"id": str(node_id)},
            )
            return node
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set node preferences",
                {"error": str(e), "id": str(node_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_node(self, node_id: Any) -> str:
        tag = f"{self.tag_class}.remove_node"
        try:
            node = await self.get_node(node_id)
            await self.control.unregister(node.device_id)
            await self.repo.delete_node_by_id(node_id)
            await self.log.info(
                tag,
                "Successfully removed node",
                {"id": str(node_id), "device_id": node.device_id},
            )
            return "Node removed successfully"
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove node",
                {"error": str(e), "id": str(node_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def register_node_connection(
        self,
        device_id: str,
        connection: Any,
    ) -> None:
        tag = f"{self.tag_class}.register_node_connection"
        registered = False
        try:
            validate_non_empty_string(device_id, "device_id")
            await self._create_node_registration_if_missing(device_id)
            await self._ensure_approved_node(device_id)
            await self.control.register(device_id, connection)
            registered = True
            await self.repo.update_node_last_connected_at_by_device_id(device_id)
            await self.log.info(
                tag,
                "Successfully registered node connection",
                {"device_id": device_id},
            )
        except DomainException:
            if registered:
                await self._cleanup_failed_node_connection(device_id, connection)
            raise
        except Exception as e:
            if registered:
                await self._cleanup_failed_node_connection(device_id, connection)
            await self.log.error(
                tag,
                "Failed to register node connection",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def unregister_node_connection(
        self,
        device_id: str,
        connection: Any = None,
    ) -> None:
        tag = f"{self.tag_class}.unregister_node_connection"
        try:
            removed = await self.control.unregister(device_id, connection)
            if not removed:
                await self.log.debug(
                    tag,
                    "Skipped node disconnect timestamp because connection was already replaced or removed",
                    {"device_id": device_id},
                )
                return

            await self.repo.update_node_last_disconnected_at_by_device_id(device_id)
            await self.log.info(
                tag,
                "Successfully unregistered node connection",
                {"device_id": device_id},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to unregister node connection",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def _cleanup_failed_node_connection(
        self,
        device_id: str,
        connection: Any,
    ) -> None:
        try:
            await self.control.unregister(device_id, connection)
        except Exception:
            pass

    async def is_node_registered(self, device_id: str) -> bool:
        tag = f"{self.tag_class}.is_node_registered"
        try:
            return await self.control.is_registered(device_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to check node registration",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_registered_nodes(self) -> List[str]:
        tag = f"{self.tag_class}.get_registered_nodes"
        try:
            return await self.control.get_registered()
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get registered nodes",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def restart_node(self, device_id: str) -> None:
        tag = f"{self.tag_class}.restart_node"
        try:
            await self._ensure_approved_node(device_id)
            await self.control.restart(device_id)
            await self.repo.update_node_last_seen_at_by_device_id(device_id)
            await self.log.info(
                tag,
                "Successfully sent node restart command",
                {"device_id": device_id},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to restart node",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_ranging_record_by_addresses(
        self,
        reported_by_device_id: str,
        pan_id: int,
        source_address: int,
        destination_address: int,
        distance: float,
    ) -> None:
        tag = f"{self.tag_class}.add_ranging_record_by_addresses"
        try:
            validate_non_empty_string(reported_by_device_id, "reported_by_device_id")
            validate_uwb_value(pan_id, "pan_id")
            validate_uwb_value(source_address, "source_address")
            validate_uwb_value(destination_address, "destination_address")
            validate_non_negative_float(distance, "distance")

            network = await self.repo_node_network.read_node_network_by_pan_id(pan_id)
            source_node = await self.repo.read_node_by_network_id_and_address(
                network_id=network.id,
                address=source_address,
            )
            destination_node = await self.repo.read_node_by_network_id_and_address(
                network_id=network.id,
                address=destination_address,
            )
            if source_node.device_id != reported_by_device_id:
                raise ForbiddenDomainException(
                    "Node ranging source must match the websocket device ID."
                )

            self._ensure_approved_nodes((source_node, destination_node))
            await self.repo_record.create_record(
                label=RecordDataLabel.RANGING,
                data=RecordDataRanging(
                    source_node_device_id=source_node.device_id,
                    target_node_device_id=destination_node.device_id,
                    distance=distance,
                ),
                recorded_at=datetime.now(timezone.utc),
                metadata={
                    "pan_id": pan_id,
                    "source_address": source_address,
                    "destination_address": destination_address,
                },
            )
            await self._set_nodes_last_seen(
                (source_node.device_id, destination_node.device_id)
            )
            await self.log.debug(
                tag,
                "Successfully added ranging record by addresses",
                {
                    "reported_by_device_id": reported_by_device_id,
                    "pan_id": pan_id,
                    "source_address": source_address,
                    "destination_address": destination_address,
                    "distance": distance,
                },
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add ranging record by addresses",
                {
                    "error": str(e),
                    "reported_by_device_id": reported_by_device_id,
                    "pan_id": pan_id,
                    "source_address": source_address,
                    "destination_address": destination_address,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def _ensure_approved_node(self, device_id: str) -> Node:
        node = await self.repo.read_node_by_device_id(device_id)
        if not node.is_approved:
            raise ForbiddenDomainException("Node is not approved.")
        return node

    async def _create_node_registration_if_missing(self, device_id: str) -> None:
        try:
            await self.repo.read_node_by_device_id(device_id)
            return
        except NotFoundDomainException:
            pass

        try:
            await self.repo.create_node(
                device_id=device_id,
                name=generate_name(),
                description="Registered from node websocket connection",
            )
        except DuplicateDomainException:
            return

    async def _set_nodes_last_seen(
        self,
        device_ids: Sequence[str],
    ) -> None:
        for device_id in self._unique_device_ids(device_ids):
            await self.repo.update_node_last_seen_at_by_device_id(device_id)

    def _ensure_approved_nodes(self, nodes: Sequence[Node]) -> None:
        for node in nodes:
            if not node.is_approved:
                raise ForbiddenDomainException("Node is not approved.")

    def _unique_device_ids(self, device_ids: Sequence[str]) -> List[str]:
        unique_device_ids: List[str] = []
        seen_device_ids: set[str] = set()
        for device_id in device_ids:
            if device_id in seen_device_ids:
                continue

            unique_device_ids.append(device_id)
            seen_device_ids.add(device_id)

        return unique_device_ids
