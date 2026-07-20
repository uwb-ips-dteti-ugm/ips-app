from typing import Any, List, Optional, Tuple

from ips_app.config import env
from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.node.control import NodeControl
from ips_app.domain.contracts.repository.firmware import FirmwareRepository
from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.models.firmware import Firmware, FirmwareDeployResult
from ips_app.domain.usecases.firmware import FirmwareUsecase

from ips_app.application._shared.validator import validate_non_empty_string


class BaseFirmwareUsecase(FirmwareUsecase):
    def __init__(self, repo: FirmwareRepository, control: NodeControl, log: LeveledLogger) -> None:
        self.repo = repo
        self.control = control
        self.log = log
        self.tag_class = self.__class__.__name__

    async def upload_firmware(
        self,
        version: str,
        board_variant: str,
        content: bytes,
        checksum: str,
        created_by: Optional[Any] = None,
    ) -> Firmware:
        tag = f"{self.tag_class}/upload_firmware"
        try:
            validate_non_empty_string(version, "version")
            validate_non_empty_string(board_variant, "board_variant")
            validate_non_empty_string(checksum, "checksum")

            firmware = await self.repo.create_firmware(
                version=version,
                board_variant=board_variant,
                content=content,
                checksum=checksum,
                created_by=created_by,
            )
            await self.log.info(
                tag,
                "Successfully uploaded firmware",
                {"version": version, "board_variant": board_variant, "size": firmware.size},
            )
            return firmware
        except Exception as e:
            await self.log.error(tag, "Failed to upload firmware", {"error": str(e)})
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_firmware(self, id: Any) -> Firmware:
        tag = f"{self.tag_class}/get_firmware"
        try:
            return await self.repo.read_firmware_by_id(id)
        except Exception as e:
            await self.log.error(tag, "Failed to retrieve firmware", {"error": str(e)})
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_firmwares(
        self, page: int, limit: int, search: Optional[str] = None
    ) -> Tuple[List[Firmware], int]:
        tag = f"{self.tag_class}/get_firmwares"
        try:
            return await self.repo.read_firmwares_by_pagination(page, limit, search)
        except Exception as e:
            await self.log.error(tag, "Failed to retrieve firmwares", {"error": str(e)})
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_firmware_content(self, id: Any) -> Tuple[bytes, Firmware]:
        tag = f"{self.tag_class}/get_firmware_content"
        try:
            return await self.repo.read_firmware_content_by_id(id)
        except Exception as e:
            await self.log.error(tag, "Failed to retrieve firmware content", {"error": str(e)})
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def delete_firmware(self, id: Any) -> None:
        tag = f"{self.tag_class}/delete_firmware"
        try:
            await self.repo.delete_firmware_by_id(id)
            await self.log.info(tag, "Successfully deleted firmware", {"firmware_id": str(id)})
        except Exception as e:
            await self.log.error(tag, "Failed to delete firmware", {"error": str(e)})
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def deploy_firmware(self, id: Any) -> FirmwareDeployResult:
        tag = f"{self.tag_class}/deploy_firmware"
        try:
            firmware = await self.repo.read_firmware_by_id(id)
            download_url = f"{env.APP_PUBLIC_BASE_URL}/firmware/download?firmware_id={firmware.id}"

            device_ids = await self.control.get_registered()
            succeeded_device_ids: List[str] = []
            failed_device_ids: List[str] = []
            for device_id in device_ids:
                try:
                    await self.control.firmware_update(
                        device_id=device_id,
                        download_url=download_url,
                        version=firmware.version,
                        size=firmware.size,
                        checksum=firmware.checksum,
                    )
                    succeeded_device_ids.append(device_id)
                except DomainException:
                    failed_device_ids.append(device_id)

            result = FirmwareDeployResult(
                targeted_device_ids=device_ids,
                succeeded_device_ids=succeeded_device_ids,
                failed_device_ids=failed_device_ids,
            )
            await self.log.info(
                tag,
                "Successfully deployed firmware",
                {
                    "firmware_id": str(id),
                    "targeted_count": len(device_ids),
                    "succeeded_count": len(succeeded_device_ids),
                    "failed_count": len(failed_device_ids),
                },
            )
            return result
        except Exception as e:
            await self.log.error(tag, "Failed to deploy firmware", {"error": str(e)})
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e
