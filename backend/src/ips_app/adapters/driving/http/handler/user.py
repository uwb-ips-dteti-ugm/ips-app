from typing import Optional, List
from fastapi import Request, Response, status, HTTPException
from ips_app.ports.driving.http.user import UserHTTPPort
from ips_app.adapters.driving.http.dto.user import (
    SetUserInfoRequest,
    SetUserRoleRequest,
    SetUserStateRequest,
    SetUserStatusRequest,
    UserResponse,
    UsersResponse
)
from ips_app.adapters.driving.http.middleware.auth_jwt import get_claims

class UserHandler:
    def __init__(self, service: UserHTTPPort):
        self.service = service

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.service.get_user(user_id)
        return UserResponse.from_domain(user)

    async def get_user_me(self) -> UserResponse:
        claims = get_claims()
        if not claims:
            raise HTTPException(status_code=401, detail="Unauthorized")
        user = await self.service.get_user(claims.user_id)
        return UserResponse.from_domain(user)

    async def get_users(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
        role_id: Optional[str] = None
    ) -> UsersResponse:
        items, total = await self.service.get_users(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
            role_id=role_id
        )
        return UsersResponse.from_domain(
            items=items,
            page=page,
            limit=limit,
            total=total
        )

    async def patch_user_info(
        self,
        user_id: str,
        request: SetUserInfoRequest
    ) -> UserResponse:
        request.validate_fields()
        user = await self.service.set_user_info(
            user_id=user_id,
            name=request.name,
            bio=request.bio
        )
        return UserResponse.from_domain(user)

    async def patch_user_me_info(
        self,
        request: SetUserInfoRequest
    ) -> UserResponse:
        claims = get_claims()
        if not claims:
            raise HTTPException(status_code=401, detail="Unauthorized")
        request.validate_fields()
        user = await self.service.set_user_info(
            user_id=claims.user_id,
            name=request.name,
            bio=request.bio
        )
        return UserResponse.from_domain(user)

    async def patch_user_preferences(
        self,
        user_id: str,
        request: Request
    ) -> UserResponse:
        body = await request.body()
        user = await self.service.set_user_preferences(
            user_id=user_id,
            preferences=body
        )
        return UserResponse.from_domain(user)

    async def patch_user_me_preferences(
        self,
        request: Request
    ) -> UserResponse:
        claims = get_claims()
        if not claims:
            raise HTTPException(status_code=401, detail="Unauthorized")
        body = await request.body()
        user = await self.service.set_user_preferences(
            user_id=claims.user_id,
            preferences=body
        )
        return UserResponse.from_domain(user)

    async def patch_user_role(
        self,
        user_id: str,
        request: SetUserRoleRequest
    ) -> UserResponse:
        request.validate_fields()
        user = await self.service.set_user_role(
            user_id=user_id,
            role_id=request.role_id
        )
        return UserResponse.from_domain(user)

    async def patch_user_state(
        self,
        user_id: str,
        request: SetUserStateRequest
    ) -> UserResponse:
        user = await self.service.set_user_state(
            user_id=user_id,
            state=request.state
        )
        return UserResponse.from_domain(user)

    async def patch_user_me_state(
        self,
        request: SetUserStateRequest
    ) -> UserResponse:
        claims = get_claims()
        if not claims:
            raise HTTPException(status_code=401, detail="Unauthorized")
        user = await self.service.set_user_state(
            user_id=claims.user_id,
            state=request.state
        )
        return UserResponse.from_domain(user)

    async def patch_user_status(
        self,
        user_id: str,
        request: SetUserStatusRequest
    ) -> UserResponse:
        user = await self.service.set_user_status(
            user_id=user_id,
            status=request.status
        )
        return UserResponse.from_domain(user)

    async def delete_user(self, user_id: str) -> Response:
        message = await self.service.remove_user(user_id)
        return Response(content=message, status_code=status.HTTP_200_OK)
