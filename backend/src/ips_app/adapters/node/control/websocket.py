import asyncio
from typing import Any, Dict

from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.node import NodeCommandCode
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.node.control import ControlNode
from ips_app.utils.validator import (
    validate_positive_integer,
    validate_uwb_network_value,
)


class WebSocketNodeControl(ControlNode):
    def __init__(self, log: GenericLogging):
        self.log = log
        self.tag_class = self.__class__.__name__
        self.connections: Dict[str, Any] = {}
        self.lock = asyncio.Lock()

    async def register(self, device_id: str, connection: Any) -> None:
        tag = f"{self.tag_class}.register"
        try:
            async with self.lock:
                self.connections[device_id] = connection

            await self.log.info(
                tag,
                "Registered node control connection",
                {"device_id": device_id},
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

    async def unregister(self, device_id: str) -> None:
        tag = f"{self.tag_class}.unregister"
        try:
            async with self.lock:
                self.connections.pop(device_id, None)

            await self.log.info(
                tag,
                "Unregistered node control connection",
                {"device_id": device_id},
            )
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
        listener_pan_id: int,
        initiator_pan_id: int,
        listen_for_ms: int,
    ) -> None:
        tag = f"{self.tag_class}.listen_ranging"
        try:
            validate_uwb_network_value(listener_pan_id, "listener_pan_id")
            validate_uwb_network_value(initiator_pan_id, "initiator_pan_id")
            validate_positive_integer(
                listen_for_ms,
                "listen_for_ms",
            )
            await self._send_command(
                device_id=device_id,
                command=NodeCommandCode.LISTEN_RANGING,
                payload={
                    "listener_pan_id": listener_pan_id,
                    "initiator_pan_id": initiator_pan_id,
                    "listen_for_ms": listen_for_ms,
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
                    "listener_pan_id": listener_pan_id,
                    "initiator_pan_id": initiator_pan_id,
                    "listen_for_ms": listen_for_ms,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def initiate_ranging(
        self,
        device_id: str,
        initiator_pan_id: int,
        listener_pan_id: int,
        wait_for_ms: int,
    ) -> None:
        tag = f"{self.tag_class}.initiate_ranging"
        try:
            validate_uwb_network_value(initiator_pan_id, "initiator_pan_id")
            validate_uwb_network_value(listener_pan_id, "listener_pan_id")
            validate_positive_integer(
                wait_for_ms,
                "wait_for_ms",
            )
            await self._send_command(
                device_id=device_id,
                command=NodeCommandCode.INITIATE_RANGING,
                payload={
                    "initiator_pan_id": initiator_pan_id,
                    "listener_pan_id": listener_pan_id,
                    "wait_for_ms": wait_for_ms,
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
                    "initiator_pan_id": initiator_pan_id,
                    "listener_pan_id": listener_pan_id,
                    "wait_for_ms": wait_for_ms,
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
        await connection.send_json(
            {
                "command": int(command),
                "payload": payload,
            }
        )

    async def _read_connection(self, device_id: str) -> Any:
        async with self.lock:
            connection = self.connections.get(device_id)
        if connection is None:
            raise NotFoundDomainException(device_id, "node connections")
        return connection
