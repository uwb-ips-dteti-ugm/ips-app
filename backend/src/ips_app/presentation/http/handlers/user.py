from typing import List, Optional

from ips_app.domain.models.user import UserAccessTokenClaims, UserStatus
from ips_app.domain.usecases.user import UserUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.permission import PermissionResponse
from ips_app.presentation.http.dto.user import (
    UpdateUserInfoRequest,
    UpdateUserPreferencesRequest,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
    UserResponse,
)


class UserHandler:
    def __init__(self, usecase: UserUsecase) -> None:
        self.usecase = usecase

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.usecase.get_user_by_id(user_id)
        return UserResponse.from_domain(user)

    async def get_users(
        self,
        page: int,
        limit: int,
        search: Optional[str],
        role_id: Optional[str],
        status: Optional[UserStatus],
    ) -> PaginatedResponse[UserResponse]:
        users, total = await self.usecase.get_users(
            page=page, limit=limit, search=search, role_id=role_id, status=status
        )
        return PaginatedResponse[UserResponse](
            items=[UserResponse.from_domain(u) for u in users],
            page=page,
            limit=limit,
            total=total,
        )

    async def get_user_permissions(self, user_id: str) -> List[PermissionResponse]:
        permissions = await self.usecase.get_user_permissions(user_id)
        return [PermissionResponse.from_domain(p) for p in permissions]

    async def patch_user_info(
        self,
        user_id: str,
        request: UpdateUserInfoRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> UserResponse:
        user = await self.usecase.update_user_info(
            id=user_id,
            name=request.name,
            bio=request.bio,
            username=request.username,
            updated_by=claims.user_id if claims else None,
        )
        return UserResponse.from_domain(user)

    async def patch_user_preferences(
        self,
        user_id: str,
        request: UpdateUserPreferencesRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> UserResponse:
        user = await self.usecase.update_user_preferences(
            id=user_id,
            preferences=request.preferences,
            updated_by=claims.user_id if claims else None,
        )
        return UserResponse.from_domain(user)

    async def patch_user_role(
        self,
        user_id: str,
        request: UpdateUserRoleRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> UserResponse:
        user = await self.usecase.update_user_role(
            id=user_id,
            role_id=request.role_id,
            updated_by=claims.user_id if claims else None,
        )
        return UserResponse.from_domain(user)

    async def patch_user_status(
        self,
        user_id: str,
        request: UpdateUserStatusRequest,
        claims: Optional[UserAccessTokenClaims],
    ) -> UserResponse:
        user = await self.usecase.update_user_status(
            id=user_id,
            status=request.status,
            updated_by=claims.user_id if claims else None,
        )
        return UserResponse.from_domain(user)

    async def delete_user(self, user_id: str) -> MessageResponse:
        await self.usecase.delete_user(user_id)
        return MessageResponse(message="User deleted successfully.")
