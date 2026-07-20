from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

TItem = TypeVar("TItem", bound=BaseModel)


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    error: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str


def stringify_id(value: Optional[Any]) -> Optional[str]:
    return str(value) if value is not None else None


class AuditedResponse(BaseModel):
    created_at: datetime
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[TItem]):
    model_config = ConfigDict(extra="forbid")
    items: List[TItem]
    page: int
    limit: int
    total: int
