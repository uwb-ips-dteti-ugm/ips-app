from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from beanie import Document, Indexed
from pydantic import Field

from ips_app.domain.models.firmware import Firmware


class FirmwareDocument(Document):
    version: Annotated[str, Indexed()]
    board_variant: str
    size: int
    checksum: str
    file_id: Any

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None

    class Settings:
        name = "firmware"

    def to_domain(self) -> Firmware:
        return Firmware(
            id=self.id,
            version=self.version,
            board_variant=self.board_variant,
            size=self.size,
            checksum=self.checksum,
            file_id=self.file_id,
            created_at=self.created_at,
            created_by=self.created_by,
        )
