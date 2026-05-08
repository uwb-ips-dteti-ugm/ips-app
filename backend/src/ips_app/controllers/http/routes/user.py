from typing import List, Optional

from fastapi import APIRouter, Request

from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.controllers.http.dto.feature import FeatureAccessResponse, FeatureResponse
from ips_app.controllers.http.dto.user import (
    SetUserInfoRequest,
    SetUserRoleRequest,
    SetUserStateRequest,
    SetUserStatusRequest,
    UserResponse,
    UsersResponse,
)
from ips_app.controllers.http.handlers.user import UserHandler
from ips_app.controllers.http.middlewares.feature_guard import feature_guard
from ips_app.controllers.http.middlewares.logger import logger
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driving.http.user import UserHTTP


def create_router(
    handler: UserHandler,
    user_service: UserHTTP,
    log: GenericLogging,
) -> APIRouter:
    guard_manage = feature_guard("user/manage", user_service)
    guard_view = feature_guard("user/view", user_service)
    guard_delete = feature_guard("user/delete", user_service)

    router = APIRouter(
        prefix="/users",
        tags=["User"],
        responses={
            400: {"model": ErrorResponse, "description": "Bad Request"},
            401: {"model": ErrorResponse, "description": "Unauthorized"},
            403: {"model": ErrorResponse, "description": "Forbidden"},
            404: {"model": ErrorResponse, "description": "Not Found"},
            409: {"model": ErrorResponse, "description": "Conflict"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
        },
    )

    @router.get(
        "/me",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.get_me",
                msg_2xx="Current user fetched successfully",
                msg_4xx="Current user fetch rejected",
                msg_5xx="Current user fetch failed",
            )
        ],
    )
    async def get_user_me():
        return await handler.get_user_me()

    @router.get(
        "/me/features",
        response_model=List[FeatureResponse],
        dependencies=[
            logger(
                log,
                tag="UserRoutes.get_me_features",
                msg_2xx="Current user accessible features fetched successfully",
                msg_4xx="Current user accessible features fetch rejected",
                msg_5xx="Current user accessible features fetch failed",
            )
        ],
    )
    async def get_user_me_accessible_features():
        return await handler.get_user_me_accessible_features()

    @router.get(
        "/me/features/access",
        response_model=FeatureAccessResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.get_me_feature_access",
                msg_2xx="Current user feature access checked successfully",
                msg_4xx="Current user feature access check rejected",
                msg_5xx="Current user feature access check failed",
            )
        ],
    )
    async def get_user_me_feature_access(feature_name: str):
        return await handler.get_user_me_feature_access(feature_name)

    @router.patch(
        "/me/info",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.patch_me_info",
                msg_2xx="Current user info updated successfully",
                msg_4xx="Current user info update rejected",
                msg_5xx="Current user info update failed",
            )
        ],
    )
    async def patch_user_me_info(request: SetUserInfoRequest):
        return await handler.patch_user_me_info(request)

    @router.patch(
        "/me/preferences",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.patch_me_preferences",
                msg_2xx="Current user preferences updated successfully",
                msg_4xx="Current user preferences update rejected",
                msg_5xx="Current user preferences update failed",
            )
        ],
    )
    async def patch_user_me_preferences(request: Request):
        return await handler.patch_user_me_preferences(request)

    @router.patch(
        "/me/state",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.patch_me_state",
                msg_2xx="Current user state updated successfully",
                msg_4xx="Current user state update rejected",
                msg_5xx="Current user state update failed",
            )
        ],
    )
    async def patch_user_me_state(request: SetUserStateRequest):
        return await handler.patch_user_me_state(request)

    @router.get(
        "",
        response_model=UsersResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.get_users",
                msg_2xx="Users fetched successfully",
                msg_4xx="Users fetch rejected",
                msg_5xx="Users fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_users(
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
        role_id: Optional[str] = None,
    ):
        return await handler.get_users(
            page=page,
            limit=limit,
            cursor_id=cursor_id,
            search=search,
            role_id=role_id,
        )

    @router.get(
        "/{user_id}",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.get_user",
                msg_2xx="User fetched successfully",
                msg_4xx="User fetch rejected",
                msg_5xx="User fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_user(user_id: str):
        return await handler.get_user(user_id)

    @router.get(
        "/{user_id}/features",
        response_model=List[FeatureResponse],
        dependencies=[
            logger(
                log,
                tag="UserRoutes.get_user_features",
                msg_2xx="User accessible features fetched successfully",
                msg_4xx="User accessible features fetch rejected",
                msg_5xx="User accessible features fetch failed",
            ),
            guard_view,
        ],
    )
    async def get_user_accessible_features(user_id: str):
        return await handler.get_user_accessible_features(user_id)

    @router.get(
        "/{user_id}/features/access",
        response_model=FeatureAccessResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.get_user_feature_access",
                msg_2xx="User feature access checked successfully",
                msg_4xx="User feature access check rejected",
                msg_5xx="User feature access check failed",
            ),
            guard_view,
        ],
    )
    async def get_user_feature_access(user_id: str, feature_name: str):
        return await handler.get_user_feature_access(user_id, feature_name)

    @router.patch(
        "/{user_id}/info",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.patch_user_info",
                msg_2xx="User info updated successfully",
                msg_4xx="User info update rejected",
                msg_5xx="User info update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_user_info(user_id: str, request: SetUserInfoRequest):
        return await handler.patch_user_info(user_id, request)

    @router.patch(
        "/{user_id}/preferences",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.patch_user_preferences",
                msg_2xx="User preferences updated successfully",
                msg_4xx="User preferences update rejected",
                msg_5xx="User preferences update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_user_preferences(user_id: str, request: Request):
        return await handler.patch_user_preferences(user_id, request)

    @router.patch(
        "/{user_id}/role",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.patch_user_role",
                msg_2xx="User role updated successfully",
                msg_4xx="User role update rejected",
                msg_5xx="User role update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_user_role(user_id: str, request: SetUserRoleRequest):
        return await handler.patch_user_role(user_id, request)

    @router.patch(
        "/{user_id}/state",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.patch_user_state",
                msg_2xx="User state updated successfully",
                msg_4xx="User state update rejected",
                msg_5xx="User state update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_user_state(user_id: str, request: SetUserStateRequest):
        return await handler.patch_user_state(user_id, request)

    @router.patch(
        "/{user_id}/status",
        response_model=UserResponse,
        dependencies=[
            logger(
                log,
                tag="UserRoutes.patch_user_status",
                msg_2xx="User status updated successfully",
                msg_4xx="User status update rejected",
                msg_5xx="User status update failed",
            ),
            guard_manage,
        ],
    )
    async def patch_user_status(user_id: str, request: SetUserStatusRequest):
        return await handler.patch_user_status(user_id, request)

    @router.delete(
        "/{user_id}",
        dependencies=[
            logger(
                log,
                tag="UserRoutes.delete_user",
                msg_2xx="User deleted successfully",
                msg_4xx="User deletion rejected",
                msg_5xx="User deletion failed",
            ),
            guard_delete,
        ],
    )
    async def delete_user(user_id: str):
        return await handler.delete_user(user_id)

    return router
