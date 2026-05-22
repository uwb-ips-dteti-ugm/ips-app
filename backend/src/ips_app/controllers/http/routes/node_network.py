from typing import Optional

from fastapi import APIRouter

from ips_app.controllers.http.dto.common import ErrorResponse, MessageResponse
from ips_app.controllers.http.dto.node_network import (
    AddNodeNetworkRequest,
    NodeNetworkResponse,
    NodeNetworksResponse,
    SetNodeNetworkRequest,
)
from ips_app.controllers.http.handlers.node_network import NodeNetworkHandler
from ips_app.controllers.http.middlewares.logger import logger
from ips_app.controllers.http.middlewares.permission_check import permission_check
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driving.http.role import RoleHTTP


def create_router(
    handler: NodeNetworkHandler,
    role_service: RoleHTTP,
    log: LeveledLogging,
) -> APIRouter:
    guard_manage = permission_check(["node-network/manage"], role_service)
    guard_view = permission_check(["node-network/view"], role_service)
    guard_delete = permission_check(["node-network/delete"], role_service)

    router = APIRouter(
        prefix="/node-networks",
        tags=["Node Network"],
        responses={
            400: {"model": ErrorResponse, "description": "Bad Request"},
            401: {"model": ErrorResponse, "description": "Unauthorized"},
            403: {"model": ErrorResponse, "description": "Forbidden"},
            404: {"model": ErrorResponse, "description": "Not Found"},
            409: {"model": ErrorResponse, "description": "Conflict"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
        },
    )

    @router.post(
        "",
        response_model=NodeNetworkResponse,
        dependencies=[
            logger(
                log,
                tag="NodeNetworkRoutes.post_node_network",
                msg_2xx="Node network created successfully",
                msg_4xx="Node network creation rejected",
                msg_5xx="Node network creation failed",
            ),
            guard_manage,
        ],
    )
    async def post_node_network(request: AddNodeNetworkRequest):
        return await handler.post_node_network(request)

    @router.get(
        "",
        response_model=NodeNetworksResponse,
        dependencies=[
            logger(
                log,
                tag="NodeNetworkRoutes.get_node_networks",
                msg_2xx="Node networks fetched successfully",
                msg_4xx="Node networks fetch rejected",
                msg_5xx="Node networks fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_node_networks(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ):
        return await handler.get_node_networks(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
        )

    @router.get(
        "/pan/{pan_id}",
        response_model=NodeNetworkResponse,
        dependencies=[
            logger(
                log,
                tag="NodeNetworkRoutes.get_node_network_by_pan_id",
                msg_2xx="Node network fetched by PAN ID successfully",
                msg_4xx="Node network fetch by PAN ID rejected",
                msg_5xx="Node network fetch by PAN ID failed",
            ),
            guard_view,
        ],
    )
    async def get_node_network_by_pan_id(pan_id: int):
        return await handler.get_node_network_by_pan_id(pan_id)

    @router.get(
        "/{node_network_id}",
        response_model=NodeNetworkResponse,
        dependencies=[
            logger(
                log,
                tag="NodeNetworkRoutes.get_node_network",
                msg_2xx="Node network fetched successfully",
                msg_4xx="Node network fetch rejected",
                msg_5xx="Node network fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_node_network(node_network_id: str):
        return await handler.get_node_network(node_network_id)

    @router.patch(
        "/{node_network_id}",
        response_model=NodeNetworkResponse,
        dependencies=[
            logger(
                log,
                tag="NodeNetworkRoutes.patch_node_network",
                msg_2xx="Node network updated successfully",
                msg_4xx="Node network update rejected",
                msg_5xx="Node network update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_node_network(
        node_network_id: str,
        request: SetNodeNetworkRequest,
    ):
        return await handler.patch_node_network(node_network_id, request)

    @router.delete(
        "/{node_network_id}",
        response_model=MessageResponse,
        dependencies=[
            logger(
                log,
                tag="NodeNetworkRoutes.delete_node_network",
                msg_2xx="Node network deleted successfully",
                msg_4xx="Node network deletion rejected",
                msg_5xx="Node network deletion failed",
            ),
            guard_delete,
        ],
    )
    async def delete_node_network(node_network_id: str):
        return await handler.delete_node_network(node_network_id)

    return router
