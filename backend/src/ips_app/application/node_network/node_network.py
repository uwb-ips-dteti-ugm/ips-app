from typing import Any, List, Optional, Tuple

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.repository.node_network import NodeNetworkRepository
from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.node_network import NodeNetwork
from ips_app.domain.usecases.node_network import NodeNetworkUsecase

from ips_app.application._shared.validator import validate_description, validate_name


class BaseNodeNetworkUsecase(NodeNetworkUsecase):
    def __init__(self, repo: NodeNetworkRepository, log: LeveledLogger) -> None:
        self.repo = repo
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_node_network(
        self,
        pan_id: int,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
    ) -> NodeNetwork:
        tag = f"{self.tag_class}/create_node_network"
        try:
            validate_name(name)
            validate_description(description)
            node_network = await self.repo.create_node_network(
                pan_id=pan_id,
                name=name,
                description=description,
                created_by=created_by,
            )
            await self.log.info(
                tag,
                "Successfully created node network",
                {"id": str(node_network.id), "pan_id": pan_id},
            )
            return node_network
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create node network",
                {"error": str(e), "pan_id": pan_id},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_network_by_id(self, id: Any) -> NodeNetwork:
        tag = f"{self.tag_class}/get_node_network_by_id"
        try:
            node_network = await self.repo.read_node_network_by_id(id)
            await self.log.info(
                tag, "Successfully retrieved node network", {"id": str(id)}
            )
            return node_network
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve node network",
                {"error": str(e), "id": str(id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_network_by_pan_id(self, pan_id: int) -> NodeNetwork:
        tag = f"{self.tag_class}/get_node_network_by_pan_id"
        try:
            node_network = await self.repo.read_node_network_by_pan_id(pan_id)
            await self.log.info(
                tag, "Successfully retrieved node network", {"pan_id": pan_id}
            )
            return node_network
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve node network",
                {"error": str(e), "pan_id": pan_id},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_node_networks(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
    ) -> Tuple[List[NodeNetwork], int]:
        tag = f"{self.tag_class}/get_node_networks"
        try:
            node_networks, total = await self.repo.read_node_networks_by_pagination(
                page=page,
                limit=limit,
                search=search,
            )
            await self.log.info(
                tag,
                "Successfully retrieved node networks",
                {"page": page, "limit": limit, "total": total},
            )
            return node_networks, total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve node networks",
                {"error": str(e), "page": page, "limit": limit},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_network(
        self,
        id: Any,
        pan_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
    ) -> NodeNetwork:
        tag = f"{self.tag_class}/update_node_network"
        try:
            if name is not None:
                validate_name(name)
            if description is not None:
                validate_description(description)
            node_network = await self.repo.update_node_network_by_id(
                id=id,
                pan_id=pan_id,
                name=name,
                description=description,
                updated_by=updated_by,
            )
            await self.log.info(
                tag, "Successfully updated node network", {"id": str(id)}
            )
            return node_network
        except Exception as e:
            await self.log.error(
                tag, "Failed to update node network", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def delete_node_network(self, id: Any) -> None:
        tag = f"{self.tag_class}/delete_node_network"
        try:
            await self.repo.delete_node_network_by_id(id)
            await self.log.info(
                tag, "Successfully deleted node network", {"id": str(id)}
            )
        except Exception as e:
            await self.log.error(
                tag, "Failed to delete node network", {"error": str(e), "id": str(id)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e
