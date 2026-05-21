import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ips_app_old.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app_old.domain.models.node import Node, NodeStatus
from ips_app_old.domain.models.record import RecordDataLabel, RecordDataRanging
from ips_app_old.domain.ports.driven.logging.generic import GenericLogging
from ips_app_old.domain.ports.driven.node.control import ControlNode
from ips_app_old.domain.ports.driven.repository.node import NodeRepository
from ips_app_old.domain.ports.driven.repository.record import RecordRepository
from ips_app_old.domain.ports.driving.http.node import NodeHTTP
from ips_app_old.utils.namegen import generate_name
from ips_app_old.utils.validator import (
    validate_non_empty_string,
    validate_optional_non_negative_float,
    validate_uwb_network_value,
)


class BaseNodeHTTP(NodeHTTP):
    def __init__(
        self,
        repo: NodeRepository,
        repo_record: RecordRepository,
        control: ControlNode,
        log: GenericLogging,
    ):
        self.repo = repo
        self.repo_record = repo_record
        self.control = control
        self.log = log
        self.tag_class = self.__class__.__name__

    async def add_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
    ) -> Node:
        tag = f"{self.tag_class}.add_node"
        try:
            node = await self.repo.create_node(
                device_id=device_id,
                name=name,
                description=description,
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

    async def get_nodes(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
    ) -> Tuple[List[Node], int]:
        tag = f"{self.tag_class}.get_nodes"
        try:
            return await self.repo.read_nodes_by_pagination(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
                status=status,
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
    ) -> Node:
        tag = f"{self.tag_class}.set_node_info"
        try:
            await self.repo.update_node_info_by_id(
                id=node_id,
                name=name,
                description=description,
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

    async def set_node_preferences(self, node_id: Any, preferences: bytes) -> Node:
        tag = f"{self.tag_class}.set_node_preferences"
        try:
            preferences_dict = json.loads(preferences)
            await self.repo.update_node_preferences_by_id(
                id=node_id,
                preferences=preferences_dict,
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
        try:
            validate_non_empty_string(device_id, "device_id")
            await self._create_node_registration_if_missing(device_id)
            await self._ensure_approved_node(device_id)
            await self.control.register(device_id, connection)
            await self.repo.update_node_last_connected_at_by_device_id(device_id)
            await self.log.info(
                tag,
                "Successfully registered node connection",
                {"device_id": device_id},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to register node connection",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def unregister_node_connection(self, device_id: str) -> None:
        tag = f"{self.tag_class}.unregister_node_connection"
        try:
            await self.control.unregister(device_id)
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

    async def add_ranging_record(
        self,
        source_node_device_id: Optional[str],
        target_node_device_id: Optional[str],
        distance: Optional[float],
        recorded_at: datetime,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        tag = f"{self.tag_class}.add_ranging_record"
        try:
            validate_optional_non_negative_float(distance, "distance")
            await self._ensure_approved_nodes(
                (source_node_device_id, target_node_device_id)
            )
            await self.repo_record.create_record(
                label=RecordDataLabel.RANGING,
                data=RecordDataRanging(
                    source_node_device_id=source_node_device_id,
                    target_node_device_id=target_node_device_id,
                    distance=distance,
                ),
                recorded_at=recorded_at,
                metadata=metadata,
            )
            await self._set_nodes_last_seen(
                (source_node_device_id, target_node_device_id)
            )
            await self.log.info(
                tag,
                "Successfully added ranging record",
                {
                    "source_node_device_id": source_node_device_id,
                    "target_node_device_id": target_node_device_id,
                    "distance": distance,
                    "recorded_at": recorded_at.isoformat(),
                },
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add ranging record",
                {
                    "error": str(e),
                    "source_node_device_id": source_node_device_id,
                    "target_node_device_id": target_node_device_id,
                    "recorded_at": recorded_at.isoformat(),
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def add_ranging_record_by_pan_ids(
        self,
        reported_by_device_id: str,
        source_pan_id: int,
        destination_pan_id: int,
        distance: Optional[float],
    ) -> None:
        tag = f"{self.tag_class}.add_ranging_record_by_pan_ids"
        try:
            validate_non_empty_string(reported_by_device_id, "reported_by_device_id")
            validate_uwb_network_value(source_pan_id, "source_pan_id")
            validate_uwb_network_value(destination_pan_id, "destination_pan_id")
            validate_optional_non_negative_float(distance, "distance")

            source_node = await self.repo.read_node_by_pan_id(source_pan_id)
            destination_node = await self.repo.read_node_by_pan_id(destination_pan_id)
            if source_node.device_id != reported_by_device_id:
                raise ForbiddenDomainException(
                    "Node ranging source must match the websocket device ID."
                )

            await self.add_ranging_record(
                source_node_device_id=source_node.device_id,
                target_node_device_id=destination_node.device_id,
                distance=distance,
                recorded_at=datetime.now(timezone.utc),
                metadata={
                    "source_pan_id": source_pan_id,
                    "destination_pan_id": destination_pan_id,
                },
            )
            await self.log.info(
                tag,
                "Successfully added ranging record by PAN IDs",
                {
                    "reported_by_device_id": reported_by_device_id,
                    "source_pan_id": source_pan_id,
                    "destination_pan_id": destination_pan_id,
                    "distance": distance,
                },
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add ranging record by PAN IDs",
                {
                    "error": str(e),
                    "reported_by_device_id": reported_by_device_id,
                    "source_pan_id": source_pan_id,
                    "destination_pan_id": destination_pan_id,
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

    async def _ensure_approved_nodes(
        self,
        device_ids: Sequence[Optional[str]],
    ) -> None:
        for device_id in self._unique_device_ids(device_ids):
            await self._ensure_approved_node(device_id)

    async def _set_nodes_last_seen(
        self,
        device_ids: Sequence[Optional[str]],
    ) -> None:
        for device_id in self._unique_device_ids(device_ids):
            await self.repo.update_node_last_seen_at_by_device_id(device_id)

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
