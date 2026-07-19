from typing import Optional

from fastapi import APIRouter, Depends, Query, WebSocket

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.node import NodeStatus
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.node import (
    CreateNodeRequest,
    NodeRegistrationResponse,
    NodeResponse,
    RegisteredNodesResponse,
    UpdateNodeInfoRequest,
    UpdateNodeNetworkAssignmentRequest,
    UpdateNodePreferencesRequest,
    UpdateNodeStatusRequest,
)
from ips_app.presentation.http.handlers.node import NodeHandler
from ips_app.presentation.http.middlewares.auth_jwt import get_claims
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import permission_check


def create_router(
    handler: NodeHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_manage = permission_check(["node/manage"], role_usecase)
    guard_view = permission_check(["node/view"], role_usecase)
    guard_delete = permission_check(["node/delete"], role_usecase)

    router = APIRouter(prefix="/nodes", tags=["Node"])

    @router.websocket("/ws/{device_id}")
    async def connect_node_websocket(device_id: str, websocket: WebSocket) -> None:
        await handler.connect_node_websocket(device_id, websocket)

    @router.post(
        "",
        response_model=NodeResponse,
        dependencies=[logger(log, "NodeRoutes/post_node"), guard_manage],
    )
    async def post_node(
        request: CreateNodeRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> NodeResponse:
        return await handler.post_node(request, claims)

    @router.get(
        "",
        response_model=PaginatedResponse[NodeResponse],
        dependencies=[logger(log, "NodeRoutes/get_nodes"), guard_view],
    )
    async def get_nodes(
        page: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        search: Optional[str] = Query(None),
        status: Optional[NodeStatus] = Query(None),
        network_id: Optional[str] = Query(None),
        address: Optional[int] = Query(None, ge=0, le=0xFFFF),
        is_online: Optional[bool] = Query(None),
    ) -> PaginatedResponse[NodeResponse]:
        return await handler.get_nodes(
            page, limit, search, status, network_id, address, is_online
        )

    @router.get(
        "/registered",
        response_model=RegisteredNodesResponse,
        dependencies=[logger(log, "NodeRoutes/get_registered_nodes"), guard_view],
    )
    async def get_registered_nodes() -> RegisteredNodesResponse:
        return await handler.get_registered_nodes()

    @router.get(
        "/registered/{device_id}",
        response_model=NodeRegistrationResponse,
        dependencies=[logger(log, "NodeRoutes/get_node_registration"), guard_view],
    )
    async def get_node_registration(device_id: str) -> NodeRegistrationResponse:
        return await handler.get_node_registration(device_id)

    @router.get(
        "/device/{device_id}",
        response_model=NodeResponse,
        dependencies=[logger(log, "NodeRoutes/get_node_by_device_id"), guard_view],
    )
    async def get_node_by_device_id(device_id: str) -> NodeResponse:
        return await handler.get_node_by_device_id(device_id)

    @router.get(
        "/network/{network_id}/address/{address}",
        response_model=NodeResponse,
        dependencies=[
            logger(log, "NodeRoutes/get_node_by_network_address"), guard_view
        ],
    )
    async def get_node_by_network_address(network_id: str, address: int) -> NodeResponse:
        return await handler.get_node_by_network_address(network_id, address)

    @router.post(
        "/{device_id}/restart",
        response_model=MessageResponse,
        dependencies=[logger(log, "NodeRoutes/post_node_restart"), guard_manage],
    )
    async def post_node_restart(device_id: str) -> MessageResponse:
        return await handler.post_node_restart(device_id)

    @router.get(
        "/{node_id}",
        response_model=NodeResponse,
        dependencies=[logger(log, "NodeRoutes/get_node"), guard_view],
    )
    async def get_node(node_id: str) -> NodeResponse:
        return await handler.get_node(node_id)

    @router.patch(
        "/{node_id}/info",
        response_model=NodeResponse,
        dependencies=[logger(log, "NodeRoutes/patch_node_info"), guard_manage],
    )
    async def patch_node_info(
        node_id: str,
        request: UpdateNodeInfoRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> NodeResponse:
        return await handler.patch_node_info(node_id, request, claims)

    @router.patch(
        "/{node_id}/network",
        response_model=NodeResponse,
        dependencies=[logger(log, "NodeRoutes/patch_node_network"), guard_manage],
    )
    async def patch_node_network(
        node_id: str,
        request: UpdateNodeNetworkAssignmentRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> NodeResponse:
        return await handler.patch_node_network(node_id, request, claims)

    @router.patch(
        "/{node_id}/status",
        response_model=NodeResponse,
        dependencies=[logger(log, "NodeRoutes/patch_node_status"), guard_manage],
    )
    async def patch_node_status(
        node_id: str,
        request: UpdateNodeStatusRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> NodeResponse:
        return await handler.patch_node_status(node_id, request, claims)

    @router.patch(
        "/{node_id}/preferences",
        response_model=NodeResponse,
        dependencies=[logger(log, "NodeRoutes/patch_node_preferences"), guard_manage],
    )
    async def patch_node_preferences(
        node_id: str,
        request: UpdateNodePreferencesRequest,
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> NodeResponse:
        return await handler.patch_node_preferences(node_id, request, claims)

    @router.delete(
        "/{node_id}",
        response_model=MessageResponse,
        dependencies=[logger(log, "NodeRoutes/delete_node"), guard_delete],
    )
    async def delete_node(node_id: str) -> MessageResponse:
        return await handler.delete_node(node_id)

    return router
