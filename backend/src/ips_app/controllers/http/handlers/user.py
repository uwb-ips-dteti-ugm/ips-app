from typing import List, Optional, Union

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.feature import FeatureAccessResponse, FeatureResponse
from ips_app.controllers.http.dto.user import (
    SetUserInfoRequest,
    SetUserRoleRequest,
    SetUserStateRequest,
    SetUserStatusRequest,
    UserResponse,
    UsersResponse,
)
from ips_app.controllers.http.handlers.exception import handle_exception
from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.ports.driving.http.user import UserHTTP


class UserHandler:
    def __init__(self, service: UserHTTP):
        self.service = service

    def _handle_exception(self, error: Exception) -> JSONResponse:
        return handle_exception(error)

    async def get_user(self, user_id: str) -> Union[UserResponse, JSONResponse]:
        try:
            user = await self.service.get_user(user_id)
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def get_user_me(self) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )
            user = await self.service.get_user(claims.user_id)
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def get_users(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
        role_id: Optional[str] = None,
    ) -> Union[UsersResponse, JSONResponse]:
        try:
            items, total = await self.service.get_users(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
                role_id=role_id,
            )
            return UsersResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_info(
        self,
        user_id: str,
        request: SetUserInfoRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            request.validate_fields()
            user = await self.service.set_user_info(
                user_id=user_id,
                name=request.name,
                bio=request.bio,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_me_info(
        self,
        request: SetUserInfoRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            request.validate_fields()
            user = await self.service.set_user_info(
                user_id=claims.user_id,
                name=request.name,
                bio=request.bio,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_preferences(
        self,
        user_id: str,
        request: Request,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            body = await request.body()
            user = await self.service.set_user_preferences(
                user_id=user_id,
                preferences=body,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_me_preferences(
        self,
        request: Request,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            body = await request.body()
            user = await self.service.set_user_preferences(
                user_id=claims.user_id,
                preferences=body,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_role(
        self,
        user_id: str,
        request: SetUserRoleRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            request.validate_fields()
            user = await self.service.set_user_role(
                user_id=user_id,
                role_id=request.role_id,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_state(
        self,
        user_id: str,
        request: SetUserStateRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            user = await self.service.set_user_state(
                user_id=user_id,
                state=request.state,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_me_state(
        self,
        request: SetUserStateRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            user = await self.service.set_user_state(
                user_id=claims.user_id,
                state=request.state,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_user_status(
        self,
        user_id: str,
        request: SetUserStatusRequest,
    ) -> Union[UserResponse, JSONResponse]:
        try:
            user = await self.service.set_user_status(
                user_id=user_id,
                status=request.status,
            )
            return UserResponse.from_domain(user)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_user(self, user_id: str) -> Union[Response, JSONResponse]:
        try:
            message = await self.service.remove_user(user_id)
            return Response(content=message, status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)

    async def get_user_accessible_features(
        self,
        user_id: str,
    ) -> Union[List[FeatureResponse], JSONResponse]:
        try:
            features = await self.service.get_accessible_features(user_id=user_id)
            return [FeatureResponse.from_domain(feature) for feature in features]
        except Exception as e:
            return self._handle_exception(e)

    async def get_user_me_accessible_features(
        self,
    ) -> Union[List[FeatureResponse], JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            features = await self.service.get_accessible_features(
                user_id=claims.user_id,
            )
            return [FeatureResponse.from_domain(feature) for feature in features]
        except Exception as e:
            return self._handle_exception(e)

    async def get_user_feature_access(
        self,
        user_id: str,
        feature_name: str,
    ) -> Union[FeatureAccessResponse, JSONResponse]:
        try:
            can_access = await self.service.can_access_feature_by_name(
                user_id=user_id,
                feature_name=feature_name,
            )
            return FeatureAccessResponse(
                feature_name=feature_name,
                can_access=can_access,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def get_user_me_feature_access(
        self,
        feature_name: str,
    ) -> Union[FeatureAccessResponse, JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )

            can_access = await self.service.can_access_feature_by_name(
                user_id=claims.user_id,
                feature_name=feature_name,
            )
            return FeatureAccessResponse(
                feature_name=feature_name,
                can_access=can_access,
            )
        except Exception as e:
            return self._handle_exception(e)
