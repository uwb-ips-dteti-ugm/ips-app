from typing import Optional, List, Union
from fastapi import Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from ips_app.ports.driving.http.feature import FeatureHTTPPort
from ips_app.domain.models.exception import (
    NotFoundException,
    DuplicateException,
    ValidatorException,
)
from ips_app.adapters.driving.http.dto.feature import (
    AddFeatureRequest,
    SetFeatureRequest,
    FeatureResponse,
    FeaturesResponse
)
from ips_app.adapters.driving.http.dto.permission import PermissionResponse
from ips_app.adapters.driving.http.dto.common import PermissionIdsRequest, ErrorResponse
from ips_app.adapters.driving.http.middleware.auth_jwt import get_claims

class FeatureHandler:
    def __init__(self, service: FeatureHTTPPort):
        self.service = service

    def _handle_exception(self, e: Exception) -> JSONResponse:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "Internal server error"

        if isinstance(e, ValidatorException):
            status_code = status.HTTP_400_BAD_REQUEST
            message = str(e)
        elif isinstance(e, NotFoundException):
            status_code = status.HTTP_404_NOT_FOUND
            message = f"Resource '{e.data_name}' in '{e.group_name}' not found"
        elif isinstance(e, DuplicateException):
            status_code = status.HTTP_409_CONFLICT
            message = f"Resource '{e.data_name}' in '{e.group_name}' already exists"
        elif isinstance(e, HTTPException):
            status_code = e.status_code
            message = str(e.detail)
        
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(error=message).model_dump()
        )

    async def post_feature(self, request: AddFeatureRequest) -> Union[FeatureResponse, JSONResponse]:
        try:
            request.validate_fields()
            feature = await self.service.add_feature(
                name=request.name,
                description=request.description
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def get_feature(self, feature_id: str) -> Union[FeatureResponse, JSONResponse]:
        try:
            feature = await self.service.get_feature(feature_id)
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def get_features(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> Union[FeaturesResponse, JSONResponse]:
        try:
            items, total = await self.service.get_features(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search
            )
            return FeaturesResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_feature(
        self,
        feature_id: str,
        request: SetFeatureRequest
    ) -> Union[FeatureResponse, JSONResponse]:
        try:
            request.validate_fields()
            feature = await self.service.set_feature(
                feature_id=feature_id,
                name=request.name,
                description=request.description
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_feature_preferences(
        self,
        feature_id: str,
        request: Request
    ) -> Union[FeatureResponse, JSONResponse]:
        try:
            body = await request.body()
            feature = await self.service.set_feature_preferences(
                feature_id=feature_id,
                preferences=body
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_feature(self, feature_id: str) -> Union[Response, JSONResponse]:
        try:
            message = await self.service.remove_feature(feature_id)
            return Response(content=message, status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)

    async def post_feature_permissions(
        self,
        feature_id: str,
        request: PermissionIdsRequest
    ) -> Union[FeatureResponse, JSONResponse]:
        try:
            request.validate_fields()
            feature = await self.service.add_permissions_to_feature(
                feature_id=feature_id,
                permission_ids=request.permission_ids
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_feature_permissions(
        self,
        feature_id: str,
        request: PermissionIdsRequest
    ) -> Union[FeatureResponse, JSONResponse]:
        try:
            request.validate_fields()
            feature = await self.service.remove_permissions_from_feature(
                feature_id=feature_id,
                permission_ids=request.permission_ids
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def get_feature_permissions(self, feature_id: str) -> Union[List[PermissionResponse], JSONResponse]:
        try:
            permissions = await self.service.get_feature_permissions(feature_id)
            return [PermissionResponse.from_domain(p) for p in permissions]
        except Exception as e:
            return self._handle_exception(e)

    async def get_feature_me_accessible(self) -> Union[List[FeatureResponse], JSONResponse]:
        try:
            claims = get_claims()
            if not claims:
                raise HTTPException(status_code=401, detail="Unauthorized")
            features = await self.service.get_accessible_features(user_id=claims.user_id)
            return [FeatureResponse.from_domain(f) for f in features]
        except Exception as e:
            return self._handle_exception(e)
