import json
from inspect import isawaitable
from typing import Any, Dict, Optional, Union

from fastapi import Request, WebSocketDisconnect, status
from fastapi.responses import JSONResponse

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
from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.node import NodeStatus
from ips_app.domain.models.record import RecordDataLabel
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driving.http.node import NodeHTTP


class NodeHandler:
    def __init__(self, service: NodeHTTP, log: LeveledLogging):
        self.tag_class = self.__class__.__name__
        self.service = service
        self.log = log

    async def post_node(
        self,
        request: AddNodeRequest,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            node = await self.service.add_node(
                device_id=request.device_id,
                name=request.name,
                description=request.description,
                network_id=request.network_id,
                address=request.address,
                preferences=request.preferences,
                created_by=claims.user_id if claims else None,
            )
            return NodeResponse.from_domain(node)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, DuplicateDomainException):
                if e.data_label == "network address":
                    error = "Another node already uses this network address."
                else:
                    error = "A node with this device ID already exists. Please choose another device ID."
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The selected node network does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while creating the node. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while creating the node. Please try again."
                ).model_dump(),
            )

    async def get_node(self, node_id: str) -> Union[NodeResponse, JSONResponse]:
        try:
            node = await self.service.get_node(node_id)
            return NodeResponse.from_domain(node)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error="Node not found.").model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading the node. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the node. Please try again."
                ).model_dump(),
            )

    async def get_node_by_device_id(
        self,
        device_id: str,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            node = await self.service.get_node_by_device_id(device_id)
            return NodeResponse.from_domain(node)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="No node uses this device ID."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading the node. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the node. Please try again."
                ).model_dump(),
            )

    async def get_node_by_network_address(
        self,
        network_id: str,
        address: int,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            node = await self.service.get_node_by_network_address(
                network_id=network_id,
                address=address,
            )
            return NodeResponse.from_domain(node)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="No node uses this network address."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading the node. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the node. Please try again."
                ).model_dump(),
            )

    async def get_nodes(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
        status_filter: Optional[NodeStatus] = None,
        network_id: Optional[str] = None,
        address: Optional[int] = None,
        is_online: Optional[bool] = None,
    ) -> Union[NodesResponse, JSONResponse]:
        try:
            items, total = await self.service.get_nodes(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
                status=status_filter,
                network_id=network_id,
                address=address,
                is_online=is_online,
            )
            return NodesResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total,
            )
        except Exception as e:
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading nodes. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading nodes. Please try again."
                ).model_dump(),
            )

    async def patch_node_info(
        self,
        node_id: str,
        request: SetNodeInfoRequest,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            node = await self.service.set_node_info(
                node_id=node_id,
                name=request.name,
                description=request.description,
                updated_by=claims.user_id if claims else None,
            )
            return NodeResponse.from_domain(node)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The node you want to update does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating the node. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating the node. Please try again."
                ).model_dump(),
            )

    async def patch_node_network_assignment(
        self,
        node_id: str,
        request: SetNodeNetworkAssignmentRequest,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            node = await self.service.set_node_network_assignment(
                node_id=node_id,
                network_id=request.network_id,
                address=request.address,
                updated_by=claims.user_id if claims else None,
            )
            return NodeResponse.from_domain(node)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, DuplicateDomainException):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content=ErrorResponse(
                        error="Another node already uses this network address."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "node networks":
                    error = "The selected node network does not exist."
                else:
                    error = "The node network assignment could not be updated because the node does not exist."
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating the node network assignment. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating the node network assignment. Please try again."
                ).model_dump(),
            )

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
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The node status could not be updated because the node does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating the node status. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating the node status. Please try again."
                ).model_dump(),
            )

    async def patch_node_preferences(
        self,
        node_id: str,
        request: Request,
    ) -> Union[NodeResponse, JSONResponse]:
        try:
            claims = get_claims()
            try:
                preferences = await request.json()
            except Exception as error:
                raise ValidatorDomainException(
                    "Preferences must be valid JSON."
                ) from error
            if not isinstance(preferences, dict):
                raise ValidatorDomainException(
                    "Preferences must be a JSON object."
                )
            node = await self.service.set_node_preferences(
                node_id=node_id,
                preferences=preferences,
                updated_by=claims.user_id if claims else None,
            )
            return NodeResponse.from_domain(node)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The node preferences could not be updated because the node does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating node preferences. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating node preferences. Please try again."
                ).model_dump(),
            )

    async def delete_node(self, node_id: str) -> Union[MessageResponse, JSONResponse]:
        try:
            message = await self.service.remove_node(node_id)
            return MessageResponse(message=message)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The node you want to delete does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while deleting the node. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while deleting the node. Please try again."
                ).model_dump(),
            )

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
                str(e),
            )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="This node is not approved yet, so it cannot connect."
                    ).model_dump(),
                )
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while connecting the node. Please try again."
                ).model_dump(),
            )
        except Exception:
            await self._reject_node_connection(
                connection,
                status.WS_1011_INTERNAL_ERROR,
                "Something went wrong while connecting the node.",
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while connecting the node. Please try again."
                ).model_dump(),
            )
        finally:
            if registered:
                try:
                    await self.service.unregister_node_connection(
                        device_id,
                        connection,
                    )
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
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while checking the node connection. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while checking the node connection. Please try again."
                ).model_dump(),
            )

    async def get_registered_nodes(
        self,
    ) -> Union[RegisteredNodesResponse, JSONResponse]:
        try:
            device_ids = await self.service.get_registered_nodes()
            return RegisteredNodesResponse(data=device_ids)
        except Exception as e:
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading connected nodes. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading connected nodes. Please try again."
                ).model_dump(),
            )

    async def post_node_restart(
        self,
        device_id: str,
    ) -> Union[MessageResponse, JSONResponse]:
        try:
            await self.service.restart_node(device_id)
            return MessageResponse(message="Node restart requested successfully")
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "node connections":
                    error = "The node is not connected right now, so it cannot be restarted."
                else:
                    error = "The node you want to restart does not exist."
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="This node is not approved yet, so it cannot be restarted."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while restarting the node. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while restarting the node. Please try again."
                ).model_dump(),
            )

    async def post_ranging_record(
        self,
        request: AddRangingRecordByAddressesRequest,
    ) -> Union[MessageResponse, JSONResponse]:
        try:
            request.validate_fields()
            await self.service.add_ranging_record_by_addresses(
                reported_by_device_id=request.reported_by_device_id,
                pan_id=request.pan_id,
                source_address=request.source_address,
                destination_address=request.destination_address,
                distance=request.distance,
            )
            return MessageResponse(message="Ranging record added successfully")
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                if e.group_name == "node networks":
                    error = "The reported PAN ID does not match any node network."
                else:
                    error = "The ranging record could not be added because one of the nodes does not exist."
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error=error).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="The ranging record can only be added by approved nodes in the selected network."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while adding the ranging record. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while adding the ranging record. Please try again."
                ).model_dump(),
            )

    async def _reject_node_connection(
        self,
        connection: Any,
        code: int,
        reason: str = "",
    ) -> None:
        close = getattr(connection, "close", None)
        if close is None:
            return

        result = close(code=code, reason=reason[:120])
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
            raise ValidatorDomainException(
                "Node websocket message must be valid JSON."
            ) from e

        if not isinstance(message, dict):
            raise ValidatorDomainException(
                "Node websocket message must be a JSON object."
            )

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

        if message.get("label") == "error":
            await self._handle_error_message(device_id, message)
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

        pan_id = self._read_required_integer(data, "pan_id")
        source_address = self._read_required_integer(data, "source_address")
        destination_address = self._read_required_integer(
            data,
            "destination_address",
        )
        distance = self._read_required_float(data, "distance")

        try:
            await self.service.add_ranging_record_by_addresses(
                reported_by_device_id=device_id,
                pan_id=pan_id,
                source_address=source_address,
                destination_address=destination_address,
                distance=distance,
            )
        except DomainException as e:
            await self.log.warn(
                f"{self.tag_class}._handle_ranging_message",
                "Rejected node ranging report",
                {
                    "device_id": device_id,
                    "pan_id": pan_id,
                    "source_address": source_address,
                    "destination_address": destination_address,
                    "distance": distance,
                    "error": str(e),
                },
            )

    async def _handle_error_message(
        self,
        device_id: str,
        message: Dict[str, Any],
    ) -> None:
        data = message.get("data") or {}
        if not isinstance(data, dict):
            raise ValidatorDomainException("Node error message data must be an object.")

        error = data.get("message")
        if not isinstance(error, str) or not error.strip():
            raise ValidatorDomainException(
                "Node error message must include a non-empty message."
            )

        await self.log.debug(
            f"{self.tag_class}._handle_error_message",
            "Node reported an error",
            {
                "device_id": device_id,
                "pan_id": data.get("pan_id"),
                "source_address": data.get("source_address"),
                "destination_address": data.get("destination_address"),
                "error": error,
            },
        )

    def _read_required_integer(self, data: Dict[str, Any], field: str) -> int:
        value = data.get(field)
        if value is None:
            raise ValidatorDomainException(f"'{field}' is required.")
        try:
            return int(value)
        except (TypeError, ValueError) as e:
            raise ValidatorDomainException(f"'{field}' must be an integer.") from e

    def _read_required_float(self, data: Dict[str, Any], field: str) -> float:
        value = data.get(field)
        if value is None:
            raise ValidatorDomainException(f"'{field}' is required.")
        try:
            parsed_value = float(value)
        except (TypeError, ValueError) as e:
            raise ValidatorDomainException(f"'{field}' must be a number.") from e
        if parsed_value < 0:
            raise ValidatorDomainException(
                f"'{field}' must be greater than or equal to 0."
            )
        return parsed_value
