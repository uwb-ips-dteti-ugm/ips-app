from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from ips_app.domain.models.firmware import Firmware, FirmwareDeployResult


class FirmwareUsecase(ABC):
    @abstractmethod
    async def upload_firmware(
        self,
        version: str,
        board_variant: str,
        content: bytes,
        checksum: str,
        created_by: Optional[Any] = None,
    ) -> Firmware: ...

    @abstractmethod
    async def get_firmware(self, id: Any) -> Firmware: ...

    @abstractmethod
    async def get_firmwares(
        self, page: int, limit: int, search: Optional[str] = None
    ) -> Tuple[List[Firmware], int]: ...

    @abstractmethod
    async def get_firmware_content(self, id: Any) -> Tuple[bytes, Firmware]: ...

    @abstractmethod
    async def delete_firmware(self, id: Any) -> None: ...

    @abstractmethod
    async def deploy_firmware(self, id: Any) -> FirmwareDeployResult: ...
