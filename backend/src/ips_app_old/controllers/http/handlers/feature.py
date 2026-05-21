from typing import List, Optional, Union

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from ips_app_old.controllers.http.dto.common import PermissionIdsRequest
from ips_app_old.controllers.http.dto.feature import (
    AddFeatureRequest,
    FeatureResponse,
    FeaturesResponse,
    SetFeatureRequest,
)
from ips_app_old.controllers.http.dto.permission import PermissionResponse
from ips_app_old.controllers.http.handlers.exception import handle_exception
from ips_app_old.domain.ports.driving.http.feature import FeatureHTTP


class FeatureHandler:
    def __init__(self, service: FeatureHTTP):
        self.service = service

    def _handle_exception(self, error: Exception) -> JSONResponse:
        return handle_exception(error)

    async def post_feature(
        self,
        request: AddFeatureRequest,
    ) -> Union[FeatureResponse, JSONResponse]:
        try:
            request.validate_fields()
            feature = await self.service.add_feature(
                name=request.name,
                description=request.description,
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def get_feature(
        self,
        feature_id: str,
    ) -> Union[FeatureResponse, JSONResponse]:
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
        search: Optional[str] = None,
    ) -> Union[FeaturesResponse, JSONResponse]:
        try:
            items, total = await self.service.get_features(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
            )
            return FeaturesResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total,
            )
        except Exception as e:
            return self._handle_exception(e)

    async def patch_feature(
        self,
        feature_id: str,
        request: SetFeatureRequest,
    ) -> Union[FeatureResponse, JSONResponse]:
        try:
            request.validate_fields()
            feature = await self.service.set_feature(
                feature_id=feature_id,
                name=request.name,
                description=request.description,
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def patch_feature_preferences(
        self,
        feature_id: str,
        request: Request,
    ) -> Union[FeatureResponse, JSONResponse]:
        try:
            body = await request.body()
            feature = await self.service.set_feature_preferences(
                feature_id=feature_id,
                preferences=body,
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_feature(
        self,
        feature_id: str,
    ) -> Union[Response, JSONResponse]:
        try:
            message = await self.service.remove_feature(feature_id)
            return Response(content=message, status_code=status.HTTP_200_OK)
        except Exception as e:
            return self._handle_exception(e)

    async def post_feature_permissions(
        self,
        feature_id: str,
        request: PermissionIdsRequest,
    ) -> Union[FeatureResponse, JSONResponse]:
        try:
            request.validate_fields()
            feature = await self.service.add_permissions_to_feature(
                feature_id=feature_id,
                permission_ids=request.permission_ids,
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_feature_permissions(
        self,
        feature_id: str,
        request: PermissionIdsRequest,
    ) -> Union[FeatureResponse, JSONResponse]:
        try:
            request.validate_fields()
            feature = await self.service.remove_permissions_from_feature(
                feature_id=feature_id,
                permission_ids=request.permission_ids,
            )
            return FeatureResponse.from_domain(feature)
        except Exception as e:
            return self._handle_exception(e)

    async def get_feature_permissions(
        self,
        feature_id: str,
    ) -> Union[List[PermissionResponse], JSONResponse]:
        try:
            permissions = await self.service.get_feature_permissions(feature_id)
            return [
                PermissionResponse.from_domain(permission)
                for permission in permissions
            ]
        except Exception as e:
            return self._handle_exception(e)
