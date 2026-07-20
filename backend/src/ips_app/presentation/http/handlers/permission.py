from typing import Optional

from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.permission import PermissionUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.permission import (
    CreatePermissionRequest,
    PermissionResponse,
    UpdatePermissionPreferencesRequest,
    UpdatePermissionRequest,
)


class PermissionHandler:
    def __init__(self, usecase: PermissionUsecase) -> None:
        self.usecase = usecase

    async def post_permission(
        self,
        request: CreatePermissionRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> PermissionResponse:
        permission = await self.usecase.create_permission(
            name=request.name,
            description=request.description,
            created_by=claims.user_id if claims else None,
        )
        return PermissionResponse.from_domain(permission)

    async def get_permission(self, permission_id: str) -> PermissionResponse:
        permission = await self.usecase.get_permission_by_id(permission_id)
        return PermissionResponse.from_domain(permission)

    async def get_permissions(
        self,
        page: int,
        limit: int,
        search: Optional[str],
    ) -> PaginatedResponse[PermissionResponse]:
        permissions, total = await self.usecase.get_permissions(
            page=page, limit=limit, search=search
        )
        return PaginatedResponse[PermissionResponse](
            items=[PermissionResponse.from_domain(p) for p in permissions],
            page=page,
            limit=limit,
            total=total,
        )

    async def patch_permission(
        self,
        permission_id: str,
        request: UpdatePermissionRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> PermissionResponse:
        permission = await self.usecase.update_permission(
            id=permission_id,
            name=request.name,
            description=request.description,
            updated_by=claims.user_id if claims else None,
        )
        return PermissionResponse.from_domain(permission)

    async def patch_permission_preferences(
        self,
        permission_id: str,
        request: UpdatePermissionPreferencesRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> PermissionResponse:
        permission = await self.usecase.update_permission_preferences(
            id=permission_id,
            preferences=request.preferences,
            updated_by=claims.user_id if claims else None,
        )
        return PermissionResponse.from_domain(permission)

    async def delete_permission(self, permission_id: str) -> MessageResponse:
        await self.usecase.delete_permission(permission_id)
        return MessageResponse(message="Permission deleted successfully.")
