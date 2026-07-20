from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from ips_app.domain.models.firmware import Firmware


class FirmwareRepository(ABC):
    @abstractmethod
    async def create_firmware(
        self,
        version: str,
        board_variant: str,
        content: bytes,
        checksum: str,
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Firmware: ...

    @abstractmethod
    async def read_firmware_by_id(self, id: Any, session: Optional[Any] = None) -> Firmware: ...

    @abstractmethod
    async def read_firmwares_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[Firmware], int]: ...

    @abstractmethod
    async def read_firmware_content_by_id(
        self, id: Any, session: Optional[Any] = None
    ) -> Tuple[bytes, Firmware]: ...

    @abstractmethod
    async def delete_firmware_by_id(self, id: Any, session: Optional[Any] = None) -> None: ...
