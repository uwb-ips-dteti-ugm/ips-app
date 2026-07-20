from typing import Optional, Tuple

from ips_app.domain.models.firmware import Firmware
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.firmware import FirmwareUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.firmware import FirmwareDeployResponse, FirmwareResponse


class FirmwareHandler:
    def __init__(self, usecase: FirmwareUsecase) -> None:
        self.usecase = usecase

    async def post_firmware(
        self,
        version: str,
        board_variant: str,
        checksum: str,
        content: bytes,
        claims: Optional[UserAccessTokenClaims],
    ) -> FirmwareResponse:
        firmware = await self.usecase.upload_firmware(
            version=version,
            board_variant=board_variant,
            content=content,
            checksum=checksum,
            created_by=claims.user_id if claims else None,
        )
        return FirmwareResponse.from_domain(firmware)

    async def get_firmwares(
        self,
        page: int,
        limit: int,
        search: Optional[str],
    ) -> PaginatedResponse[FirmwareResponse]:
        firmwares, total = await self.usecase.get_firmwares(page=page, limit=limit, search=search)
        return PaginatedResponse[FirmwareResponse](
            items=[FirmwareResponse.from_domain(f) for f in firmwares],
            page=page,
            limit=limit,
            total=total,
        )

    async def get_firmware_download(self, firmware_id: str) -> Tuple[bytes, Firmware]:
        return await self.usecase.get_firmware_content(firmware_id)

    async def delete_firmware(self, firmware_id: str) -> MessageResponse:
        await self.usecase.delete_firmware(firmware_id)
        return MessageResponse(message="Firmware deleted successfully.")

    async def post_firmware_deploy(self, firmware_id: str) -> FirmwareDeployResponse:
        result = await self.usecase.deploy_firmware(firmware_id)
        return FirmwareDeployResponse(
            targeted_count=len(result.targeted_device_ids),
            succeeded_count=len(result.succeeded_device_ids),
            failed_device_ids=result.failed_device_ids,
            skipped_count=len(result.skipped_device_ids),
        )
