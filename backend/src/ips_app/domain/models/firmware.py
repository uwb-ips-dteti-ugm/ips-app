from datetime import datetime, timezone
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Firmware(BaseModel):
    id: Optional[Any] = None
    version: str = Field(..., min_length=1)
    board_variant: str = Field(..., min_length=1)
    size: int = Field(..., gt=0)
    checksum: str = Field(..., min_length=64, max_length=64)
    file_id: Any = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[Any] = None


class FirmwareDeployResult(BaseModel):
    targeted_device_ids: List[str] = Field(default_factory=list)
    succeeded_device_ids: List[str] = Field(default_factory=list)
    failed_device_ids: List[str] = Field(default_factory=list)
    skipped_device_ids: List[str] = Field(default_factory=list)
