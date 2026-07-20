from typing import Any, Dict, List, Optional, Tuple

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.node.control import NodeControl
from ips_app.domain.contracts.repository.node import NodeRepository
from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.domain.usecases.node import NodeUsecase

from ips_app.application._shared.validator import (
    validate_description,
    validate_name,
    validate_node_network_assignment,
    validate_preferences,
)


class BaseNodeUsecase(NodeUsecase):
    def __init__(
        self,
        repo: NodeRepository,
        control: NodeControl,
        log: LeveledLogger,
    ) -> None:
        self.repo = repo
        self.control = control
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        created_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}/create_node"
        try:
            validate_name(name)
            validate_description(description)
            validate_node_network_assignment(network_id, address)
            if preferences is not None:
                validate_preferences(preferences)
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
                "Successfully created node",
                {"id": str(node.id), "device_id": device_id},
            )
            return node
        except Exception as e:
            await self.log.error(
                tag, "Failed to create node", {"error": str(e), "device_id": device_id}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_by_id(self, id: Any) -> Node:
        tag = f"{self.tag_class}/get_node_by_id"
        try:
            node = await self.repo.read_node_by_id(id)
            await self.log.info(tag, "Successfully retrieved node", {"id": str(id)})
            return node
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve node", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_by_device_id(self, device_id: str) -> Node:
        tag = f"{self.tag_class}/get_node_by_device_id"
        try:
            node = await self.repo.read_node_by_device_id(device_id)
            await self.log.info(
                tag, "Successfully retrieved node", {"device_id": device_id}
            )
            return node
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve node",
                {"error": str(e), "device_id": device_id},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_by_network_address(
        self,
        network_id: Any,
        address: int,
    ) -> Node:
        tag = f"{self.tag_class}/get_node_by_network_address"
        try:
            node = await self.repo.read_node_by_network_id_and_address(
                network_id=network_id,
                address=address,
            )
            await self.log.info(
                tag,
                "Successfully retrieved node",
                {"network_id": str(network_id), "address": address},
            )
            return node
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve node",
                {"error": str(e), "network_id": str(network_id), "address": address},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_nodes(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        is_online: Optional[bool] = None,
    ) -> Tuple[List[Node], int]:
        tag = f"{self.tag_class}/get_nodes"
        try:
            nodes, total = await self.repo.read_nodes_by_pagination(
                page=page,
                limit=limit,
                search=search,
                status=status,
                network_id=network_id,
                address=address,
                is_online=is_online,
            )
            await self.log.info(
                tag,
                "Successfully retrieved nodes",
                {"page": page, "limit": limit, "total": total},
            )
            return nodes, total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve nodes",
                {"error": str(e), "page": page, "limit": limit},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_info(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}/update_node_info"
        try:
            if name is not None:
                validate_name(name)
            if description is not None:
                validate_description(description)
            node = await self.repo.update_node_info_by_id(
                id=id,
                name=name,
                description=description,
                updated_by=updated_by,
            )
            await self.log.info(tag, "Successfully updated node info", {"id": str(id)})
            return node
        except Exception as e:
            await self.log.error(
                tag, "Failed to update node info", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_network_assignment(
        self,
        id: Any,
        network_id: Optional[Any],
        address: Optional[int],
        updated_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}/update_node_network_assignment"
        try:
            validate_node_network_assignment(network_id, address)
            node = await self.repo.update_node_network_assignment_by_id(
                id=id,
                network_id=network_id,
                address=address,
                updated_by=updated_by,
            )
            await self.log.info(
                tag,
                "Successfully updated node network assignment",
                {"id": str(id), "network_id": str(network_id)},
            )
            return node
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node network assignment",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_status(
        self,
        id: Any,
        status: NodeStatus,
        updated_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}/update_node_status"
        try:
            node = await self.repo.update_node_status_by_id(
                id=id,
                status=status,
                updated_by=updated_by,
            )
            if node.status != NodeStatus.APPROVED:
                await self._unregister_inactive_node(node)
            await self.log.info(
                tag,
                "Successfully updated node status",
                {"id": str(id), "status": str(status)},
            )
            return node
        except Exception as e:
            await self.log.error(
                tag, "Failed to update node status", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_preferences(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
    ) -> Node:
        tag = f"{self.tag_class}/update_node_preferences"
        try:
            validate_preferences(preferences)
            node = await self.repo.update_node_preferences_by_id(
                id=id,
                preferences=preferences,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully updated node preferences", {"id": str(id)}
            )
            return node
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node preferences",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def delete_node(self, id: Any) -> None:
        tag = f"{self.tag_class}/delete_node"
        try:
            node = await self.repo.read_node_by_id(id)
            await self._unregister_node_connection(node.device_id)
            await self.repo.delete_node_by_id(id)
            await self.log.info(tag, "Successfully deleted node", {"id": str(id)})
        except Exception as e:
            await self.log.error(
                tag, "Failed to delete node", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def _unregister_inactive_node(self, node: Node) -> None:
        await self._unregister_node_connection(node.device_id)

    async def _unregister_node_connection(self, device_id: str) -> None:
        try:
            await self.control.unregister(device_id)
        except Exception:
            pass
