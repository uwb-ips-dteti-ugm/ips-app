import asyncio
from inspect import isawaitable
from typing import Any, Dict

from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.node import NodeCommandCode
from ips_app.domain.ports.driven.control.node import NodeControl
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.utils.validator import validate_positive_integer, validate_uwb_value


class WebSocketNodeControl(NodeControl):
    def __init__(self, log: LeveledLogging):
        self.log = log
        self.tag_class = self.__class__.__name__
        self.connections: Dict[str, Any] = {}
        self.lock = asyncio.Lock()

    async def register(self, device_id: str, connection: Any) -> None:
        tag = f"{self.tag_class}.register"
        try:
            replaced_connection = None
            async with self.lock:
                replaced_connection = self.connections.get(device_id)
                self.connections[device_id] = connection

            if (
                replaced_connection is not None
                and replaced_connection is not connection
            ):
                await self._close_connection(device_id, replaced_connection)

            await self.log.info(
                tag,
                "Registered node control connection",
                {
                    "device_id": device_id,
                    "replaced": replaced_connection is not None,
                },
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to register node control connection",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def unregister(self, device_id: str, connection: Any = None) -> bool:
        tag = f"{self.tag_class}.unregister"
        try:
            removed_connection = None
            async with self.lock:
                current_connection = self.connections.get(device_id)
                if connection is None or current_connection is connection:
                    removed_connection = self.connections.pop(device_id, None)

            removed = removed_connection is not None
            if removed:
                await self._close_connection(device_id, removed_connection)

            await self.log.info(
                tag,
                "Unregistered node control connection",
                {"device_id": device_id, "removed": removed},
            )
            return removed
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to unregister node control connection",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def is_registered(self, device_id: str) -> bool:
        tag = f"{self.tag_class}.is_registered"
        try:
            async with self.lock:
                return device_id in self.connections
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to check node control connection",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def get_registered(self) -> list[str]:
        tag = f"{self.tag_class}.get_registered"
        try:
            async with self.lock:
                return list(self.connections.keys())
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to list node control connections",
                {"error": str(e)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def restart(self, device_id: str) -> None:
        tag = f"{self.tag_class}.restart"
        try:
            await self._send_command(
                device_id=device_id,
                command=NodeCommandCode.RESTART,
                payload={},
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to send node restart command",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def listen_ranging(
        self,
        device_id: str,
        pan_id: int,
        listener_address: int,
        initiator_address: int,
        timeout_uus: int,
    ) -> None:
        tag = f"{self.tag_class}.listen_ranging"
        try:
            validate_uwb_value(pan_id, "pan_id")
            validate_uwb_value(listener_address, "listener_address")
            validate_uwb_value(initiator_address, "initiator_address")
            validate_positive_integer(timeout_uus, "timeout_uus")
            await self._send_command(
                device_id=device_id,
                command=NodeCommandCode.LISTEN_RANGING,
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
            await self.log.error(
                tag,
                "Failed to send node listen ranging command",
                {
                    "error": str(e),
                    "device_id": device_id,
                    "pan_id": pan_id,
                    "listener_address": listener_address,
                    "initiator_address": initiator_address,
                    "timeout_uus": timeout_uus,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def initiate_ranging(
        self,
        device_id: str,
        pan_id: int,
        initiator_address: int,
        listener_address: int,
        timeout_uus: int,
    ) -> None:
        tag = f"{self.tag_class}.initiate_ranging"
        try:
            validate_uwb_value(pan_id, "pan_id")
            validate_uwb_value(initiator_address, "initiator_address")
            validate_uwb_value(listener_address, "listener_address")
            validate_positive_integer(timeout_uus, "timeout_uus")
            await self._send_command(
                device_id=device_id,
                command=NodeCommandCode.INITIATE_RANGING,
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
            await self.log.error(
                tag,
                "Failed to send node initiate ranging command",
                {
                    "error": str(e),
                    "device_id": device_id,
                    "pan_id": pan_id,
                    "initiator_address": initiator_address,
                    "listener_address": listener_address,
                    "timeout_uus": timeout_uus,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

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
            await self.log.warn(
                f"{self.tag_class}._send_command",
                "Removed failed node control connection",
                {
                    "device_id": device_id,
                    "command": int(command),
                    "error": str(e),
                },
            )
            raise NotFoundDomainException(device_id, "node connections") from e

    async def _read_connection(self, device_id: str) -> Any:
        async with self.lock:
            connection = self.connections.get(device_id)
        if connection is None:
            raise NotFoundDomainException(device_id, "node connections")
        return connection

    async def _close_connection(self, device_id: str, connection: Any) -> None:
        close = getattr(connection, "close", None)
        if close is None:
            return

        try:
            result = close(code=1000)
            if isawaitable(result):
                await result
        except Exception as e:
            await self.log.debug(
                f"{self.tag_class}._close_connection",
                "Node control connection close failed or was already closed",
                {"device_id": device_id, "error": str(e)},
            )
