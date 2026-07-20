import json
from inspect import isawaitable
from typing import Any, Dict, Optional

from fastapi import status
from fastapi.websockets import WebSocketDisconnect

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.exception import DomainException, ValidatorDomainException
from ips_app.domain.models.node import NodeStatus
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.node import NodeUsecase
from ips_app.domain.usecases.node_connection import NodeConnectionUsecase
from ips_app.domain.usecases.ranging import RangingUsecase
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


class NodeHandler:
    def __init__(
        self,
        usecase: NodeUsecase,
        connection_usecase: NodeConnectionUsecase,
        ranging_usecase: RangingUsecase,
        log: LeveledLogger,
    ) -> None:
        self.usecase = usecase
        self.connection_usecase = connection_usecase
        self.ranging_usecase = ranging_usecase
        self.log = log
        self.tag_class = self.__class__.__name__

    async def post_node(
        self,
        request: CreateNodeRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> NodeResponse:
        node = await self.usecase.create_node(
            device_id=request.device_id,
            name=request.name,
            description=request.description,
            network_id=request.network_id,
            address=request.address,
            preferences=request.preferences,
            created_by=claims.user_id if claims else None,
        )
        return NodeResponse.from_domain(node)

    async def get_node(self, node_id: str) -> NodeResponse:
        node = await self.usecase.get_node_by_id(node_id)
        return NodeResponse.from_domain(node)

    async def get_node_by_device_id(self, device_id: str) -> NodeResponse:
        node = await self.usecase.get_node_by_device_id(device_id)
        return NodeResponse.from_domain(node)

    async def get_node_by_network_address(
        self, network_id: str, address: int
    ) -> NodeResponse:
        node = await self.usecase.get_node_by_network_address(network_id, address)
        return NodeResponse.from_domain(node)

    async def get_nodes(
        self,
        page: int,
        limit: int,
        search: Optional[str],
        status: Optional[NodeStatus],
        network_id: Optional[str],
        address: Optional[int],
        is_online: Optional[bool],
    ) -> PaginatedResponse[NodeResponse]:
        nodes, total = await self.usecase.get_nodes(
            page=page,
            limit=limit,
            search=search,
            status=status,
            network_id=network_id,
            address=address,
            is_online=is_online,
        )
        return PaginatedResponse[NodeResponse](
            items=[NodeResponse.from_domain(n) for n in nodes],
            page=page,
            limit=limit,
            total=total,
        )

    async def patch_node_info(
        self,
        node_id: str,
        request: UpdateNodeInfoRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> NodeResponse:
        node = await self.usecase.update_node_info(
            id=node_id,
            name=request.name,
            description=request.description,
            updated_by=claims.user_id if claims else None,
        )
        return NodeResponse.from_domain(node)

    async def patch_node_network(
        self,
        node_id: str,
        request: UpdateNodeNetworkAssignmentRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> NodeResponse:
        node = await self.usecase.update_node_network_assignment(
            id=node_id,
            network_id=request.network_id,
            address=request.address,
            updated_by=claims.user_id if claims else None,
        )
        return NodeResponse.from_domain(node)

    async def patch_node_status(
        self,
        node_id: str,
        request: UpdateNodeStatusRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> NodeResponse:
        node = await self.usecase.update_node_status(
            id=node_id,
            status=request.status,
            updated_by=claims.user_id if claims else None,
        )
        return NodeResponse.from_domain(node)

    async def patch_node_preferences(
        self,
        node_id: str,
        request: UpdateNodePreferencesRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> NodeResponse:
        node = await self.usecase.update_node_preferences(
            id=node_id,
            preferences=request.preferences,
            updated_by=claims.user_id if claims else None,
        )
        return NodeResponse.from_domain(node)

    async def delete_node(self, node_id: str) -> MessageResponse:
        await self.usecase.delete_node(node_id)
        return MessageResponse(message="Node deleted successfully.")

    async def get_registered_nodes(self) -> RegisteredNodesResponse:
        device_ids = await self.connection_usecase.get_connected_device_ids()
        return RegisteredNodesResponse(device_ids=device_ids)

    async def get_node_registration(self, device_id: str) -> NodeRegistrationResponse:
        is_connected = await self.connection_usecase.is_connected(device_id)
        return NodeRegistrationResponse(device_id=device_id, is_connected=is_connected)

    async def post_node_restart(self, device_id: str) -> MessageResponse:
        await self.connection_usecase.restart_node(device_id)
        return MessageResponse(message="Node restart command sent successfully.")

    async def connect_node_websocket(
        self,
        device_id: str,
        connection: Any,
        board_variant: Optional[str] = None,
    ) -> None:
        tag = f"{self.tag_class}/connect_node_websocket"
        registered = False
        try:
            await self.connection_usecase.register_connection(
                device_id, connection, board_variant
            )
            registered = True

            await self._accept_node_connection(connection)
            await self._run_node_connection_loop(device_id, connection)
        except WebSocketDisconnect:
            pass
        except DomainException as e:
            await self._reject_node_connection(
                connection, status.WS_1008_POLICY_VIOLATION, str(e)
            )
        except Exception as e:
            await self.log.error(
                tag,
                "Node websocket connection failed",
                {"error": str(e), "device_id": device_id},
            )
            await self._reject_node_connection(
                connection,
                status.WS_1011_INTERNAL_ERROR,
                "Something went wrong while connecting the node.",
            )
        finally:
            if registered:
                try:
                    await self.connection_usecase.unregister_connection(device_id, connection)
                except Exception:
                    pass

    async def _run_node_connection_loop(self, device_id: str, connection: Any) -> None:
        while True:
            message = await self._receive_node_message(connection)
            if message is None:
                return
            await self._handle_node_message(device_id, message)

    async def _receive_node_message(self, connection: Any) -> Optional[Dict[str, Any]]:
        receive = getattr(connection, "receive", None)
        if receive is None:
            return None

        result = receive()
        raw_message = await result if isawaitable(result) else result

        if not isinstance(raw_message, dict):
            raise ValidatorDomainException("Node websocket message must be an object.")

        if raw_message.get("type") == "websocket.disconnect":
            return None
        if "label" in raw_message:
            return raw_message

        raw_payload = raw_message.get("text")
        if raw_payload is None and raw_message.get("bytes") is not None:
            raw_payload = raw_message["bytes"].decode("utf-8")
        if raw_payload is None:
            return {}

        try:
            message = json.loads(raw_payload)
        except json.JSONDecodeError as e:
            raise ValidatorDomainException(
                "Node websocket message must be valid JSON."
            ) from e
        if not isinstance(message, dict):
            raise ValidatorDomainException("Node websocket message must be a JSON object.")
        return message

    async def _handle_node_message(self, device_id: str, message: Dict[str, Any]) -> None:
        if not message:
            return
        if message.get("label") == "ranging":
            await self._handle_ranging_message(device_id, message)
            return
        if message.get("label") == "error":
            await self._handle_error_message(device_id, message)
            return
        if message.get("label") == "ota":
            await self._handle_ota_message(device_id, message)
            return
        if message.get("event") in {"heartbeat", "ack"}:
            return

        raise ValidatorDomainException("Unsupported node websocket message.")

    async def _handle_ranging_message(self, device_id: str, message: Dict[str, Any]) -> None:
        tag = f"{self.tag_class}/_handle_ranging_message"
        try:
            data = message.get("data") or {}
            await self.ranging_usecase.report_ranging_measurement(
                reported_by_device_id=device_id,
                pan_id=data["pan_id"],
                source_address=data["source_address"],
                destination_address=data["destination_address"],
                distance=data["distance"],
            )
        except DomainException as e:
            await self.log.warn(
                tag,
                "Rejected ranging measurement from node websocket",
                {"error": str(e), "device_id": device_id},
            )

    async def _handle_error_message(self, device_id: str, message: Dict[str, Any]) -> None:
        await self.log.debug(
            f"{self.tag_class}/_handle_error_message",
            "Received error message from node websocket",
            {"device_id": device_id, "message": message},
        )

    async def _handle_ota_message(self, device_id: str, message: Dict[str, Any]) -> None:
        await self.log.debug(
            f"{self.tag_class}/_handle_ota_message",
            "Received OTA status message from node websocket",
            {"device_id": device_id, "message": message},
        )

    async def _accept_node_connection(self, connection: Any) -> None:
        accept = getattr(connection, "accept", None)
        if accept is None:
            return
        result = accept()
        if isawaitable(result):
            await result

    async def _reject_node_connection(self, connection: Any, code: int, reason: str) -> None:
        close = getattr(connection, "close", None)
        if close is None:
            return
        try:
            result = close(code=code, reason=reason)
            if isawaitable(result):
                await result
        except Exception:
            pass
