from typing import Any

from pydantic import BaseModel, Field


class RangingNodePair(BaseModel):
    network_id: Any
    pan_id: int = Field(..., ge=0, le=0xFFFF)
    listener_device_id: str
    listener_address: int = Field(..., ge=0, le=0xFFFF)
    initiator_device_id: str
    initiator_address: int = Field(..., ge=0, le=0xFFFF)
    cycle_done: bool
