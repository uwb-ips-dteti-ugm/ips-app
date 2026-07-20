from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.user import UserAccessTokenClaims
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.dto.common import MessageResponse, PaginatedResponse
from ips_app.presentation.http.dto.firmware import FirmwareDeployResponse, FirmwareResponse
from ips_app.presentation.http.handlers.firmware import FirmwareHandler
from ips_app.presentation.http.middlewares.auth_jwt import get_claims
from ips_app.presentation.http.middlewares.logger import logger
from ips_app.presentation.http.middlewares.permission_check import permission_check


def create_router(
    handler: FirmwareHandler,
    role_usecase: RoleUsecase,
    log: LeveledLogger,
) -> APIRouter:
    guard_manage = permission_check(["firmware/manage"], role_usecase)
    guard_view = permission_check(["firmware/view"], role_usecase)
    guard_delete = permission_check(["firmware/delete"], role_usecase)

    router = APIRouter(prefix="/firmware", tags=["Firmware"])

    @router.post(
        "",
        response_model=FirmwareResponse,
        dependencies=[logger(log, "FirmwareRoutes/post_firmware"), guard_manage],
    )
    async def post_firmware(
        file: UploadFile = File(...),
        version: str = Form(...),
        board_variant: str = Form(...),
        checksum: str = Form(...),
        claims: Optional[UserAccessTokenClaims] = Depends(get_claims),
    ) -> FirmwareResponse:
        content = await file.read()
        return await handler.post_firmware(version, board_variant, checksum, content, claims)

    @router.get(
        "",
        response_model=PaginatedResponse[FirmwareResponse],
        dependencies=[logger(log, "FirmwareRoutes/get_firmwares"), guard_view],
    )
    async def get_firmwares(
        page: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        search: Optional[str] = Query(None),
    ) -> PaginatedResponse[FirmwareResponse]:
        return await handler.get_firmwares(page, limit, search)

    # Intentionally unauthenticated and undecorated with the logger/guard dependencies used by
    # every other route in this app: the ESP32 has no bearer-token mechanism for plain HTTP, so
    # this route must stay reachable without a JWT. It is listed verbatim in JwtMiddleware's
    # excluded_paths (exact-path match) in composition/main/launcher.py.
    @router.get("/download")
    async def get_firmware_download(firmware_id: str = Query(...)) -> Response:
        content, firmware = await handler.get_firmware_download(firmware_id)
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{firmware.version}-{firmware.board_variant}.bin"'
            },
        )

    @router.delete(
        "/{firmware_id}",
        response_model=MessageResponse,
        dependencies=[logger(log, "FirmwareRoutes/delete_firmware"), guard_delete],
    )
    async def delete_firmware(firmware_id: str) -> MessageResponse:
        return await handler.delete_firmware(firmware_id)

    @router.post(
        "/{firmware_id}/deploy",
        response_model=FirmwareDeployResponse,
        dependencies=[logger(log, "FirmwareRoutes/post_firmware_deploy"), guard_manage],
    )
    async def post_firmware_deploy(firmware_id: str) -> FirmwareDeployResponse:
        return await handler.post_firmware_deploy(firmware_id)

    return router
