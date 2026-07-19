from typing import Optional

from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.node_network import NodeNetworkUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.node_network import (
    CreateNodeNetworkRequest,
    NodeNetworkResponse,
    UpdateNodeNetworkRequest,
)


class NodeNetworkHandler:
    def __init__(self, usecase: NodeNetworkUsecase) -> None:
        self.usecase = usecase

    async def post_node_network(
        self,
        request: CreateNodeNetworkRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> NodeNetworkResponse:
        node_network = await self.usecase.create_node_network(
            pan_id=request.pan_id,
            name=request.name,
            description=request.description,
            created_by=claims.user_id if claims else None,
        )
        return NodeNetworkResponse.from_domain(node_network)

    async def get_node_network(self, node_network_id: str) -> NodeNetworkResponse:
        node_network = await self.usecase.get_node_network_by_id(node_network_id)
        return NodeNetworkResponse.from_domain(node_network)

    async def get_node_network_by_pan_id(self, pan_id: int) -> NodeNetworkResponse:
        node_network = await self.usecase.get_node_network_by_pan_id(pan_id)
        return NodeNetworkResponse.from_domain(node_network)

    async def get_node_networks(
        self, page: int, limit: int, search: Optional[str]
    ) -> PaginatedResponse[NodeNetworkResponse]:
        node_networks, total = await self.usecase.get_node_networks(
            page=page, limit=limit, search=search
        )
        return PaginatedResponse[NodeNetworkResponse](
            items=[NodeNetworkResponse.from_domain(n) for n in node_networks],
            page=page,
            limit=limit,
            total=total,
        )

    async def patch_node_network(
        self,
        node_network_id: str,
        request: UpdateNodeNetworkRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> NodeNetworkResponse:
        node_network = await self.usecase.update_node_network(
            id=node_network_id,
            pan_id=request.pan_id,
            name=request.name,
            description=request.description,
            updated_by=claims.user_id if claims else None,
        )
        return NodeNetworkResponse.from_domain(node_network)

    async def delete_node_network(self, node_network_id: str) -> MessageResponse:
        await self.usecase.delete_node_network(node_network_id)
        return MessageResponse(message="Node network deleted successfully.")
