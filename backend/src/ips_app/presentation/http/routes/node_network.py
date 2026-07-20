from typing import Optional

from fastapi import APIRouter, Depends, Query

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.node_network import (
    CreateNodeNetworkRequest,
    NodeNetworkResponse,
    UpdateNodeNetworkRequest,
)
from ips_app.presentation.http.handlers.node_network import NodeNetworkHandler
from ips_app.presentation.http.middlewares.auth_jwt import get_claims
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import permission_check


def create_router(
    handler: NodeNetworkHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_manage = permission_check(["node-network/manage"], role_usecase)
    guard_view = permission_check(["node-network/view"], role_usecase)
    guard_delete = permission_check(["node-network/delete"], role_usecase)

    router = APIRouter(prefix="/node-networks", tags=["NodeNetwork"])

    @router.post(
        "",
        response_model=NodeNetworkResponse,
        dependencies=[logger(log, "NodeNetworkRoutes/post_node_network"), guard_manage],
    )
    async def post_node_network(
        request: CreateNodeNetworkRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> NodeNetworkResponse:
        return await handler.post_node_network(request, claims)

    @router.get(
        "",
        response_model=PaginatedResponse[NodeNetworkResponse],
        dependencies=[logger(log, "NodeNetworkRoutes/get_node_networks"), guard_view],
    )
    async def get_node_networks(
        page: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        search: Optional[str] = Query(None),
    ) -> PaginatedResponse[NodeNetworkResponse]:
        return await handler.get_node_networks(page, limit, search)

    @router.get(
        "/pan/{pan_id}",
        response_model=NodeNetworkResponse,
        dependencies=[
            logger(log, "NodeNetworkRoutes/get_node_network_by_pan_id"), guard_view
        ],
    )
    async def get_node_network_by_pan_id(pan_id: int) -> NodeNetworkResponse:
        return await handler.get_node_network_by_pan_id(pan_id)

    @router.get(
        "/{node_network_id}",
        response_model=NodeNetworkResponse,
        dependencies=[logger(log, "NodeNetworkRoutes/get_node_network"), guard_view],
    )
    async def get_node_network(node_network_id: str) -> NodeNetworkResponse:
        return await handler.get_node_network(node_network_id)

    @router.patch(
        "/{node_network_id}",
        response_model=NodeNetworkResponse,
        dependencies=[logger(log, "NodeNetworkRoutes/patch_node_network"), guard_manage],
    )
    async def patch_node_network(
        node_network_id: str,
        request: UpdateNodeNetworkRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> NodeNetworkResponse:
        return await handler.patch_node_network(node_network_id, request, claims)

    @router.delete(
        "/{node_network_id}",
        response_model=MessageResponse,
        dependencies=[logger(log, "NodeNetworkRoutes/delete_node_network"), guard_delete],
    )
    async def delete_node_network(node_network_id: str) -> MessageResponse:
        return await handler.delete_node_network(node_network_id)

    return router
