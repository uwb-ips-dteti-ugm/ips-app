from typing import List, Optional

from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.permission import PermissionResponse
from ips_app.presentation.http.dto.role import (
    CreateRoleRequest,
    RolePermissionIdsRequest,
    RoleResponse,
    UpdateRolePreferencesRequest,
    UpdateRoleRequest,
)


class RoleHandler:
    def __init__(self, usecase: RoleUsecase) -> None:
        self.usecase = usecase

    async def post_role(
        self,
        request: CreateRoleRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> RoleResponse:
        role = await self.usecase.create_role(
            name=request.name,
            description=request.description,
            is_default=request.is_default,
            created_by=claims.user_id if claims else None,
        )
        return RoleResponse.from_domain(role)

    async def get_role(self, role_id: str) -> RoleResponse:
        role = await self.usecase.get_role_by_id(role_id)
        return RoleResponse.from_domain(role)

    async def get_default_role(self) -> RoleResponse:
        role = await self.usecase.get_default_role()
        return RoleResponse.from_domain(role)

    async def get_roles(
        self, page: int, limit: int, search: Optional[str]
    ) -> PaginatedResponse[RoleResponse]:
        roles, total = await self.usecase.get_roles(page=page, limit=limit, search=search)
        return PaginatedResponse[RoleResponse](
            items=[RoleResponse.from_domain(r) for r in roles],
            page=page,
            limit=limit,
            total=total,
        )

    async def get_role_permissions(self, role_id: str) -> List[PermissionResponse]:
        permissions = await self.usecase.get_role_permissions(role_id)
        return [PermissionResponse.from_domain(p) for p in permissions]

    async def patch_role(
        self,
        role_id: str,
        request: UpdateRoleRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> RoleResponse:
        role = await self.usecase.update_role(
            id=role_id,
            name=request.name,
            description=request.description,
            updated_by=claims.user_id if claims else None,
        )
        return RoleResponse.from_domain(role)

    async def patch_default_role(
        self, role_id: str, claims: Optional[UserAccessTokenClaims]
    ) -> RoleResponse:
        role = await self.usecase.set_default_role(
            id=role_id, updated_by=claims.user_id if claims else None
        )
        return RoleResponse.from_domain(role)

    async def patch_role_preferences(
        self,
        role_id: str,
        request: UpdateRolePreferencesRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> RoleResponse:
        role = await self.usecase.update_role_preferences(
            id=role_id,
            preferences=request.preferences,
            updated_by=claims.user_id if claims else None,
        )
        return RoleResponse.from_domain(role)

    async def delete_role(self, role_id: str) -> MessageResponse:
        await self.usecase.delete_role(role_id)
        return MessageResponse(message="Role deleted successfully.")

    async def post_role_permissions(
        self,
        role_id: str,
        request: RolePermissionIdsRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> RoleResponse:
        role = await self.usecase.add_permissions_to_role(
            id=role_id,
            permission_ids=list(request.permission_ids),
            updated_by=claims.user_id if claims else None,
        )
        return RoleResponse.from_domain(role)

    async def delete_role_permissions(
        self,
        role_id: str,
        request: RolePermissionIdsRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> RoleResponse:
        role = await self.usecase.remove_permissions_from_role(
            id=role_id,
            permission_ids=list(request.permission_ids),
            updated_by=claims.user_id if claims else None,
        )
        return RoleResponse.from_domain(role)
