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


class WebSocketNodeControl(ControlNode):
    def __init__(self, log: GenericLogging):
        self.log = log
        self.tag_class = "WebSocketNodeControl"
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
        listener_device_id: str,
        initiator_device_id: str,
        listen_for: int,
    ) -> None:
        tag = f"{self.tag_class}.listen_ranging"
        try:
            await self._send_command(
                device_id=listener_device_id,
                command=NodeCommandCode.LISTEN_RANGING,
                payload={
                    "initiator_device_id": initiator_device_id,
                    "listen_for": listen_for,
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
                    "listener_device_id": listener_device_id,
                    "initiator_device_id": initiator_device_id,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def initiate_ranging(
        self,
        initiator_device_id: str,
        target_device_id: str,
        wait_for: int,
    ) -> None:
        tag = f"{self.tag_class}.initiate_ranging"
        try:
            await self._send_command(
                device_id=initiator_device_id,
                command=NodeCommandCode.INITIATE_RANGING,
                payload={
                    "target_device_id": target_device_id,
                    "wait_for": wait_for,
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
                    "initiator_device_id": initiator_device_id,
                    "target_device_id": target_device_id,
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
