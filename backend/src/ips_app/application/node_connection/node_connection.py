from typing import Any, List, Optional

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.node.control import NodeControl
from ips_app.domain.contracts.repository.node import NodeRepository
from ips_app.domain.contracts.utility.namegen import NameGenerator
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.node import NodeStatus
from ips_app.domain.usecases.node_connection import NodeConnectionUsecase

from ips_app.application._shared.validator import validate_non_empty_string


class BaseNodeConnectionUsecase(NodeConnectionUsecase):
    def __init__(
        self,
        repo: NodeRepository,
        control: NodeControl,
        name_generator: NameGenerator,
        log: LeveledLogger,
    ) -> None:
        self.repo = repo
        self.control = control
        self.name_generator = name_generator
        self.log = log
        self.tag_class = self.__class__.__name__

    async def register_connection(
        self,
        device_id: str,
        connection: Any,
        board_variant: Optional[str] = None,
    ) -> None:
        tag = f"{self.tag_class}/register_connection"
        registered = False
        try:
            validate_non_empty_string(device_id, "device_id")
            await self._create_node_registration_if_missing(device_id, board_variant)

            node = await self.repo.read_node_by_device_id(device_id)
            if node.status != NodeStatus.APPROVED:
                raise ForbiddenDomainException("Node is not approved.")

            await self.control.register(device_id, connection)
            registered = True

            await self.repo.update_node_last_connected_at_by_device_id(
                device_id, board_variant=board_variant
            )
            await self.log.info(
                tag, "Successfully registered node connection", {"device_id": device_id}
            )
        except Exception as e:
            if registered:
                await self._unregister_quietly(device_id, connection)
            await self.log.error(
                tag,
                "Failed to register node connection",
                {"error": str(e), "device_id": device_id},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def unregister_connection(
        self,
        device_id: str,
        connection: Optional[Any] = None,
    ) -> None:
        tag = f"{self.tag_class}/unregister_connection"
        try:
            removed = await self.control.unregister(device_id, connection)
            if not removed:
                await self.log.debug(
                    tag,
                    "Skipped node disconnect timestamp because connection was already replaced or removed",
                    {"device_id": device_id},
                )
                return

            await self.repo.update_node_last_disconnected_at_by_device_id(device_id)
            await self.log.info(
                tag,
                "Successfully unregistered node connection",
                {"device_id": device_id},
            )
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to unregister node connection",
                {"error": str(e), "device_id": device_id},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def is_connected(self, device_id: str) -> bool:
        tag = f"{self.tag_class}/is_connected"
        try:
            is_connected = await self.control.is_registered(device_id)
            await self.log.info(
                tag,
                "Successfully checked node connection",
                {"device_id": device_id, "is_connected": is_connected},
            )
            return is_connected
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to check node connection",
                {"error": str(e), "device_id": device_id},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_connected_device_ids(self) -> List[str]:
        tag = f"{self.tag_class}/get_connected_device_ids"
        try:
            device_ids = await self.control.get_registered()
            await self.log.info(
                tag,
                "Successfully retrieved connected device IDs",
                {"count": len(device_ids)},
            )
            return device_ids
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve connected device IDs", {"error": str(e)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def restart_node(self, device_id: str) -> None:
        tag = f"{self.tag_class}/restart_node"
        try:
            node = await self.repo.read_node_by_device_id(device_id)
            if node.status != NodeStatus.APPROVED:
                raise ForbiddenDomainException("Node is not approved.")

            await self.control.restart(device_id)
            await self.repo.update_node_last_seen_at_by_device_id(device_id)
            await self.log.info(
                tag, "Successfully sent node restart command", {"device_id": device_id}
            )
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to send node restart command",
                {"error": str(e), "device_id": device_id},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def _create_node_registration_if_missing(
        self, device_id: str, board_variant: Optional[str] = None
    ) -> None:
        try:
            await self.repo.read_node_by_device_id(device_id)
            return
        except NotFoundDomainException:
            pass

        try:
            await self.repo.create_node(
                device_id=device_id,
                name=self.name_generator.generate(),
                description="Registered from node websocket connection",
                board_variant=board_variant,
            )
        except DuplicateDomainException:
            return

    async def _unregister_quietly(self, device_id: str, connection: Any) -> None:
        try:
            await self.control.unregister(device_id, connection)
        except Exception:
            pass
