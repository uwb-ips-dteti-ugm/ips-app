from typing import Optional

from fastapi import APIRouter, Request, WebSocket

from ips_app.controllers.http.dto.common import ErrorResponse, MessageResponse
from ips_app.controllers.http.dto.node import (
    AddNodeRequest,
    AddRangingRecordByAddressesRequest,
    NodeRegistrationResponse,
    NodeResponse,
    NodesResponse,
    RegisteredNodesResponse,
    SetNodeInfoRequest,
    SetNodeNetworkAssignmentRequest,
    SetNodeStatusRequest,
)
from ips_app.controllers.http.handlers.node import NodeHandler
from ips_app.controllers.http.middlewares.logger import logger
from ips_app.controllers.http.middlewares.permission_check import permission_check
from ips_app.domain.models.node import NodeStatus
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driving.http.role import RoleHTTP


def create_router(
    handler: NodeHandler,
    role_service: RoleHTTP,
    log: LeveledLogging,
) -> APIRouter:
    guard_manage = permission_check(["node/manage"], role_service)
    guard_view = permission_check(["node/view"], role_service)
    guard_delete = permission_check(["node/delete"], role_service)

    router = APIRouter(
        prefix="/nodes",
        tags=["Node"],
        responses={
            400: {"model": ErrorResponse, "description": "Bad Request"},
            401: {"model": ErrorResponse, "description": "Unauthorized"},
            403: {"model": ErrorResponse, "description": "Forbidden"},
            404: {"model": ErrorResponse, "description": "Not Found"},
            409: {"model": ErrorResponse, "description": "Conflict"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
        },
    )

    @router.websocket("/ws/{device_id}")
    async def connect_node_websocket(device_id: str, websocket: WebSocket):
        await handler.connect_node_websocket(device_id, websocket)

    @router.post(
        "",
        response_model=NodeResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.post_node",
                msg_2xx="Node created successfully",
                msg_4xx="Node creation rejected",
                msg_5xx="Node creation failed",
            ),
            guard_manage,
        ],
    )
    async def post_node(request: AddNodeRequest):
        return await handler.post_node(request)

    @router.get(
        "",
        response_model=NodesResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.get_nodes",
                msg_2xx="Nodes fetched successfully",
                msg_4xx="Nodes fetch rejected",
                msg_5xx="Nodes fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_nodes(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_id: Optional[str] = None,
        address: Optional[int] = None,
    ):
        return await handler.get_nodes(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
            status_filter=status,
            network_id=network_id,
            address=address,
        )

    @router.get(
        "/registered",
        response_model=RegisteredNodesResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.get_registered_nodes",
                msg_2xx="Registered nodes fetched successfully",
                msg_4xx="Registered nodes fetch rejected",
                msg_5xx="Registered nodes fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_registered_nodes():
        return await handler.get_registered_nodes()

    @router.get(
        "/registered/{device_id}",
        response_model=NodeRegistrationResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.get_node_registration",
                msg_2xx="Node registration checked successfully",
                msg_4xx="Node registration check rejected",
                msg_5xx="Node registration check failed",
            ),
            guard_view,
        ],
    )
    async def get_node_registration(device_id: str):
        return await handler.get_node_registration(device_id)

    @router.get(
        "/device/{device_id}",
        response_model=NodeResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.get_node_by_device_id",
                msg_2xx="Node fetched by device ID successfully",
                msg_4xx="Node fetch by device ID rejected",
                msg_5xx="Node fetch by device ID failed",
            ),
            guard_view,
        ],
    )
    async def get_node_by_device_id(device_id: str):
        return await handler.get_node_by_device_id(device_id)

    @router.post(
        "/device/{device_id}/restart",
        response_model=MessageResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.post_node_restart",
                msg_2xx="Node restart requested successfully",
                msg_4xx="Node restart request rejected",
                msg_5xx="Node restart request failed",
            ),
            guard_manage,
        ],
    )
    async def post_node_restart(device_id: str):
        return await handler.post_node_restart(device_id)

    @router.get(
        "/network/{network_id}/address/{address}",
        response_model=NodeResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.get_node_by_network_address",
                msg_2xx="Node fetched by network address successfully",
                msg_4xx="Node fetch by network address rejected",
                msg_5xx="Node fetch by network address failed",
            ),
            guard_view,
        ],
    )
    async def get_node_by_network_address(network_id: str, address: int):
        return await handler.get_node_by_network_address(network_id, address)

    @router.post(
        "/ranging-records",
        response_model=MessageResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.post_ranging_record",
                msg_2xx="Ranging record added successfully",
                msg_4xx="Ranging record add rejected",
                msg_5xx="Ranging record add failed",
            ),
            guard_manage,
        ],
    )
    async def post_ranging_record(request: AddRangingRecordByAddressesRequest):
        return await handler.post_ranging_record(request)

    @router.get(
        "/{node_id}",
        response_model=NodeResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.get_node",
                msg_2xx="Node fetched successfully",
                msg_4xx="Node fetch rejected",
                msg_5xx="Node fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_node(node_id: str):
        return await handler.get_node(node_id)

    @router.patch(
        "/{node_id}/info",
        response_model=NodeResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.patch_node_info",
                msg_2xx="Node info updated successfully",
                msg_4xx="Node info update rejected",
                msg_5xx="Node info update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_node_info(node_id: str, request: SetNodeInfoRequest):
        return await handler.patch_node_info(node_id, request)

    @router.patch(
        "/{node_id}/network",
        response_model=NodeResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.patch_node_network_assignment",
                msg_2xx="Node network assignment updated successfully",
                msg_4xx="Node network assignment update rejected",
                msg_5xx="Node network assignment update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_node_network_assignment(
        node_id: str,
        request: SetNodeNetworkAssignmentRequest,
    ):
        return await handler.patch_node_network_assignment(node_id, request)

    @router.patch(
        "/{node_id}/preferences",
        response_model=NodeResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.patch_node_preferences",
                msg_2xx="Node preferences updated successfully",
                msg_4xx="Node preferences update rejected",
                msg_5xx="Node preferences update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_node_preferences(node_id: str, request: Request):
        return await handler.patch_node_preferences(node_id, request)

    @router.patch(
        "/{node_id}/status",
        response_model=NodeResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.patch_node_status",
                msg_2xx="Node status updated successfully",
                msg_4xx="Node status update rejected",
                msg_5xx="Node status update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_node_status(node_id: str, request: SetNodeStatusRequest):
        return await handler.patch_node_status(node_id, request)

    @router.delete(
        "/{node_id}",
        response_model=MessageResponse,
        dependencies=[
            logger(
                log,
                tag="NodeRoutes.delete_node",
                msg_2xx="Node deleted successfully",
                msg_4xx="Node deletion rejected",
                msg_5xx="Node deletion failed",
            ),
            guard_delete,
        ],
    )
    async def delete_node(node_id: str):
        return await handler.delete_node(node_id)

    return router
