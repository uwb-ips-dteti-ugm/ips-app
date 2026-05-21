import json
from inspect import isawaitable
from typing import Any, Dict, Optional, Union

from fastapi import Request, Response, WebSocketDisconnect, status
from fastapi.responses import JSONResponse

from ips_app_old.controllers.http.dto.node import (
    AddNodeRequest,
    AddRangingRecordRequest,
    NodeRegistrationResponse,
    NodeResponse,
    NodesResponse,
    RegisteredNodesResponse,
    SetNodeInfoRequest,
    SetNodeStatusRequest,
)
from ips_app_old.controllers.http.handlers.exception import handle_exception
from ips_app_old.controllers.http.middlewares.auth_jwt import get_claims
from ips_app_old.domain.models.exception import DomainException, ValidatorDomainException
from ips_app_old.domain.models.node import NodeStatus
from ips_app_old.domain.models.record import RecordDataLabel
from ips_app_old.domain.ports.driving.http.node import NodeHTTP


class NodeHandler:
    def __init__(self, service: NodeHTTP):
        self.service = service

    def _handle_exception(self, error: Exception) -> JSONResponse:
        return handle_exception(error)

    async def post_node(
        self,
        request: AddNodeRequest,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            request.validate_fields()
            node = await self.service.add_node(
                device_id=request.device_id,
                name=request.name,
                description=request.description,
            )
            return NodeResponse.from_domain(node)
        except Exception as e:
            return self._handle_exception(e)

    async def get_node(
        self,
        node_id: str,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            node = await self.service.get_node(node_id)
            return NodeResponse.from_domain(node)
        except Exception as e:
            return self._handle_exception(e)

    async def get_node_by_device_id(
        self,
        device_id: str,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            node = await self.service.get_node_by_device_id(device_id)
            return NodeResponse.from_domain(node)
        except Exception as e:
            return self._handle_exception(e)

    async def get_nodes(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
    ) -> Union[NodesResponse, JSONResponse]:
        try:
            items, total = await self.service.get_nodes(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
                status=status,
            )
            return NodesResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_node_info(
        self,
        node_id: str,
        request: SetNodeInfoRequest,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            request.validate_fields()
            node = await self.service.set_node_info(
                node_id=node_id,
                name=request.name,
                description=request.description,
            )
            return NodeResponse.from_domain(node)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_node_status(
        self,
        node_id: str,
        request: SetNodeStatusRequest,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            claims = get_claims()
            node = await self.service.set_node_status(
                node_id=node_id,
                status=request.status,
                updated_by=claims.user_id if claims else None,
            )
            return NodeResponse.from_domain(node)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_node_preferences(
        self,
        node_id: str,
        request: Request,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            body = await request.body()
            node = await self.service.set_node_preferences(
                node_id=node_id,
                preferences=body,
            )
            return NodeResponse.from_domain(node)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_node(
        self,
        node_id: str,
    ) -> Union[Response, JSONResponse]:
        try:
            message = await self.service.remove_node(node_id)
            return Response(content=message, status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)

    async def connect_node_websocket(
        self,
        device_id: str,
        connection: Any,
    ) -> Optional[JSONResponse]:
        registered = False
        try:
            await self.service.register_node_connection(
                device_id=device_id,
                connection=connection,
            )
            registered = True
            await self._accept_node_connection(connection)
            await self._run_node_connection_loop(device_id, connection)
            return None
        except WebSocketDisconnect:
            return None
        except DomainException as e:
            await self._reject_node_connection(
                connection,
                status.WS_1008_POLICY_VIOLATION,
            )
            return self._handle_exception(e)
        except Exception as e:
            await self._reject_node_connection(
                connection,
                status.WS_1011_INTERNAL_ERROR,
            )
            return self._handle_exception(e)
        finally:
            if registered:
                try:
                    await self.service.unregister_node_connection(device_id)
                except Exception:
                    pass

    async def get_node_registration(
        self,
        device_id: str,
    ) -> Union[NodeRegistrationResponse, JSONResponse]:
        try:
            is_registered = await self.service.is_node_registered(device_id)
            return NodeRegistrationResponse(
                device_id=device_id,
                is_registered=is_registered,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def get_registered_nodes(
        self,
    ) -> Union[RegisteredNodesResponse, JSONResponse]:
        try:
            device_ids = await self.service.get_registered_nodes()
            return RegisteredNodesResponse(data=device_ids)
        except Exception as e:
            return self._handle_exception(e)

    async def post_node_restart(
        self,
        device_id: str,
    ) -> Union[Response, JSONResponse]:
        try:
            await self.service.restart_node(device_id)
            return Response(
                content="Node restart requested successfully",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def post_ranging_record(
        self,
        request: AddRangingRecordRequest,
    ) -> Union[Response, JSONResponse]:
        try:
            request.validate_fields()
            await self.service.add_ranging_record(
                source_node_device_id=request.source_node_device_id,
                target_node_device_id=request.target_node_device_id,
                distance=request.distance,
                recorded_at=request.recorded_at,
                metadata=request.metadata,
            )
            return Response(
                content="Ranging record added successfully",
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def _reject_node_connection(self, connection: Any, code: int) -> None:
        close = getattr(connection, "close", None)
        if close is None:
            return

        result = close(code=code)
        if isawaitable(result):
            await result

    async def _accept_node_connection(self, connection: Any) -> None:
        accept = getattr(connection, "accept", None)
        if accept is None:
            return

        result = accept()
        if isawaitable(result):
            await result

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
            raise ValidatorDomainException("Node websocket message must be valid JSON.") from e

        if not isinstance(message, dict):
            raise ValidatorDomainException("Node websocket message must be a JSON object.")

        return message

    async def _handle_node_message(
        self,
        device_id: str,
        message: Dict[str, Any],
    ) -> None:
        if not message:
            return

        if message.get("label") == RecordDataLabel.RANGING.value:
            await self._handle_ranging_message(device_id, message)
            return

        if message.get("event") in {"heartbeat", "ack"}:
            return

        raise ValidatorDomainException("Unsupported node websocket message.")

    async def _handle_ranging_message(
        self,
        device_id: str,
        message: Dict[str, Any],
    ) -> None:
        data = message.get("data") or {}
        if not isinstance(data, dict):
            raise ValidatorDomainException("Node ranging message data must be an object.")

        await self.service.add_ranging_record_by_pan_ids(
            reported_by_device_id=device_id,
            source_pan_id=self._read_required_integer(data, "source_pan_id"),
            destination_pan_id=self._read_required_integer(
                data,
                "destination_pan_id",
            ),
            distance=self._read_optional_float(data, "distance"),
        )

    def _read_required_integer(self, data: Dict[str, Any], field: str) -> int:
        value = data.get(field)
        if value is None:
            raise ValidatorDomainException(f"'{field}' is required.")
        try:
            return int(value)
        except (TypeError, ValueError) as e:
            raise ValidatorDomainException(f"'{field}' must be an integer.") from e

    def _read_optional_float(
        self,
        data: Dict[str, Any],
        field: str,
    ) -> Optional[float]:
        value = data.get(field)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError) as e:
            raise ValidatorDomainException(f"'{field}' must be a number.") from e
