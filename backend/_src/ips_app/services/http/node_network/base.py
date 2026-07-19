from typing import Any, List, Optional, Tuple

from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.node_network import NodeNetwork
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.node_network import (
    NodeNetworkRepository,
)
from ips_app.domain.ports.driving.http.node_network import NodeNetworkHTTP


class BaseNodeNetworkHTTP(NodeNetworkHTTP):
    def __init__(self, repo: NodeNetworkRepository, log: LeveledLogging):
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def add_node_network(
        self,
        pan_id: int,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
    ) -> NodeNetwork:
        tag = f"{self.tag_class}.add_node_network"
        try:
            node_network = await self.repo.create_node_network(
                pan_id=pan_id,
                name=name,
                description=description,
                created_by=created_by,
            )
            await self.log.info(
                tag,
                "Successfully added node network",
                {"id": str(node_network.id), "pan_id": pan_id},
            )
            return node_network
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to add node network",
                {"error": str(e), "pan_id": pan_id, "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_network(self, node_network_id: Any) -> NodeNetwork:
        tag = f"{self.tag_class}.get_node_network"
        try:
            return await self.repo.read_node_network_by_id(node_network_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get node network",
                {"error": str(e), "id": str(node_network_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_network_by_pan_id(self, pan_id: int) -> NodeNetwork:
        tag = f"{self.tag_class}.get_node_network_by_pan_id"
        try:
            return await self.repo.read_node_network_by_pan_id(pan_id)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get node network by PAN ID",
                {"error": str(e), "pan_id": pan_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_networks(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[NodeNetwork], int]:
        tag = f"{self.tag_class}.get_node_networks"
        try:
            return await self.repo.read_node_networks_by_pagination(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to get node networks",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def set_node_network(
        self,
        node_network_id: Any,
        pan_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> NodeNetwork:
        tag = f"{self.tag_class}.set_node_network"
        try:
            await self.repo.update_node_network_by_id(
                id=node_network_id,
                pan_id=pan_id,
                name=name,
                description=description,
                updated_by=updated_by,
            )
            node_network = await self.get_node_network(node_network_id)
            await self.log.info(
                tag,
                "Successfully updated node network",
                {"id": str(node_network_id)},
            )
            return node_network
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to set node network",
                {"error": str(e), "id": str(node_network_id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def remove_node_network(self, node_network_id: Any) -> str:
        tag = f"{self.tag_class}.remove_node_network"
        try:
            await self.repo.delete_node_network_by_id(node_network_id)
            await self.log.info(
                tag,
                "Successfully removed node network",
                {"id": str(node_network_id)},
            )
            return "Node network removed successfully"
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to remove node network",
                {"error": str(e), "id": str(node_network_id)},
            )
            raise UnexpectedDomainException(str(e)) from e
