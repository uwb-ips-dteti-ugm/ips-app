import asyncio
from inspect import isawaitable
from typing import Any, Dict, List, Optional, cast

from fastapi import WebSocket

from ips_app.domain.contracts.node.control import NodeControl
from ips_app.domain.models.exception import (
    DomainException,
    NodeNotConnectedDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.node import NodeCommandCode


class WebSocketNodeControl(NodeControl):
    def __init__(self) -> None:
        self.connections: Dict[str, WebSocket] = {}
        self.lock = asyncio.Lock()

    async def register(self, device_id: str, connection: Any) -> None:
        try:
            websocket_connection = cast(WebSocket, connection)
            async with self.lock:
                replaced_connection = self.connections.get(device_id)
                self.connections[device_id] = websocket_connection

            if (
                replaced_connection is not None
                and replaced_connection is not websocket_connection
            ):
                await self._close_connection(replaced_connection)
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def unregister(self, device_id: str, connection: Any = None) -> bool:
        try:
            websocket_connection = cast(Optional[WebSocket], connection)
            removed_connection = None
            async with self.lock:
                current_connection = self.connections.get(device_id)
                if websocket_connection is None or current_connection is websocket_connection:
                    removed_connection = self.connections.pop(device_id, None)

            removed = removed_connection is not None
            if removed:
                await self._close_connection(removed_connection)

            return removed
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def is_registered(self, device_id: str) -> bool:
        try:
            async with self.lock:
                return device_id in self.connections
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def get_registered(self) -> List[str]:
        try:
            async with self.lock:
                return list(self.connections.keys())
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def restart(self, device_id: str) -> None:
        try:
            await self._send_command(
                device_id=device_id,
                command=NodeCommandCode.RESTART,
                payload={},
            )
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def ranging_listen(
        self,
        device_id: str,
        pan_id: int,
        listener_address: int,
        initiator_address: int,
        timeout_uus: int,
    ) -> None:
        try:
            self._ensure_uwb_value(pan_id, "pan_id")
            self._ensure_uwb_value(listener_address, "listener_address")
            self._ensure_uwb_value(initiator_address, "initiator_address")
            self._ensure_positive_integer(timeout_uus, "timeout_uus")
            await self._send_command(
                device_id=device_id,
                command=NodeCommandCode.RANGING_LISTEN,
                payload={
                    "pan_id": pan_id,
                    "listener_address": listener_address,
                    "initiator_address": initiator_address,
                    "timeout_uus": timeout_uus,
                },
            )
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def ranging_initiate(
        self,
        device_id: str,
        pan_id: int,
        initiator_address: int,
        listener_address: int,
        timeout_uus: int,
    ) -> None:
        try:
            self._ensure_uwb_value(pan_id, "pan_id")
            self._ensure_uwb_value(initiator_address, "initiator_address")
            self._ensure_uwb_value(listener_address, "listener_address")
            self._ensure_positive_integer(timeout_uus, "timeout_uus")
            await self._send_command(
                device_id=device_id,
                command=NodeCommandCode.RANGING_INITIATE,
                payload={
                    "pan_id": pan_id,
                    "initiator_address": initiator_address,
                    "listener_address": listener_address,
                    "timeout_uus": timeout_uus,
                },
            )
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    def _ensure_uwb_value(self, value: int, field: str) -> None:
        if value < 0 or value > 0xFFFF:
            raise ValidatorDomainException(f"'{field}' must be between 0 and 65535.")

    def _ensure_positive_integer(self, value: int, field: str) -> None:
        if value <= 0:
            raise ValidatorDomainException(f"'{field}' must be greater than 0.")

    async def _send_command(
        self,
        device_id: str,
        command: NodeCommandCode,
        payload: Dict[str, Any],
    ) -> None:
        connection = await self._read_connection(device_id)
        try:
            await connection.send_json(
                {
                    "command": int(command),
                    "payload": payload,
                }
            )
        except Exception as e:
            await self.unregister(device_id, connection)
            raise NodeNotConnectedDomainException(
                f"Node '{device_id}' is not connected."
            ) from e

    async def _read_connection(self, device_id: str) -> WebSocket:
        async with self.lock:
            connection = self.connections.get(device_id)
        if connection is None:
            raise NodeNotConnectedDomainException(
                f"Node '{device_id}' is not connected."
            )
        return connection

    async def _close_connection(self, connection: WebSocket) -> None:
        close = getattr(connection, "close", None)
        if close is None:
            return

        try:
            result = close(code=1000)
            if isawaitable(result):
                await result
        except Exception:
            pass
