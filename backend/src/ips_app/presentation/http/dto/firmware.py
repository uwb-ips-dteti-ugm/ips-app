from typing import List

from pydantic import BaseModel, ConfigDict

from ips_app.domain.models.firmware import Firmware
from ips_app.presentation.http.dto.common import AuditedResponse, stringify_id


class FirmwareResponse(AuditedResponse):
    id: str
    version: str
    board_variant: str
    size: int
    checksum: str

    @classmethod
    def from_domain(cls, firmware: Firmware) -> "FirmwareResponse":
        return cls(
            id=str(firmware.id),
            version=firmware.version,
            board_variant=firmware.board_variant,
            size=firmware.size,
            checksum=firmware.checksum,
            created_at=firmware.created_at,
            created_by=stringify_id(firmware.created_by),
        )


class FirmwareDeployResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    targeted_count: int
    succeeded_count: int
    failed_device_ids: List[str]
    skipped_count: int
