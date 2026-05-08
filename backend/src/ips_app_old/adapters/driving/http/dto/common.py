from __future__ import annotations
from typing import Generic, List, TypeVar
from pydantic import BaseModel
from ips_app_old.utils.validator import validate_ids_list

T = TypeVar("T")

class ErrorResponse(BaseModel):
    error: str

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta

class PermissionIdsRequest(BaseModel):
    permission_ids: List[str]

    def validate_fields(self) -> None:
        validate_ids_list(self.permission_ids, "permission_ids")
