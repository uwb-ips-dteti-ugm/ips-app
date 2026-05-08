from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from ips_app.domain.models.exception import ValidatorDomainException
from ips_app.utils.validator import validate_ids_list


T = TypeVar("T")


class ErrorResponse(BaseModel):
    error: str = Field(..., examples=["Resource not found"])


class MessageResponse(BaseModel):
    message: str = Field(..., examples=["User removed successfully"])


class PaginationMeta(BaseModel):
    page: int = Field(..., examples=[0])
    limit: int = Field(..., examples=[10])
    total: int = Field(..., examples=[42])


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta


class PermissionIdsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permission_ids: List[str] = Field(
        ...,
        examples=[["507f1f77bcf86cd799439011"]],
    )

    def validate_fields(self) -> None:
        validate_ids_list(self.permission_ids, "permission_ids")


def validate_non_empty_string(value: str, field: str) -> None:
    if not value.strip():
        raise ValidatorDomainException(f"{field} must not be empty.")
