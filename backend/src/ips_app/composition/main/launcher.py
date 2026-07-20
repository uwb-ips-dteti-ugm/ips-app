import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from ips_app.application.auth.auth import BaseAuthUsecase
from ips_app.application.firmware.firmware import BaseFirmwareUsecase
from ips_app.application.node.node import BaseNodeUsecase
from ips_app.application.node_connection.node_connection import (
    BaseNodeConnectionUsecase,
)
from ips_app.application.node_network.node_network import BaseNodeNetworkUsecase
from ips_app.application.permission.permission import BasePermissionUsecase
from ips_app.application.ranging.ranging import BaseRangingUsecase
from ips_app.application.ranging_scheduler.ranging_scheduler import (
    BaseRangingSchedulerUsecase,
)
from ips_app.application.ranging_scheduler_config.ranging_scheduler_config import (
    BaseRangingSchedulerConfigUsecase,
)
from ips_app.application.role.role import BaseRoleUsecase
from ips_app.application.user.user import BaseUserUsecase
from ips_app.composition._shared.logger import create_logger
from ips_app.config import app as app_config
from ips_app.config import env
from ips_app.domain.models.ranging_scheduler_config import RangingSchedulerConfig
from ips_app.infrastructure.node.control.websocket import WebSocketNodeControl
from ips_app.infrastructure.repository.firmware.beanie_model import FirmwareDocument
from ips_app.infrastructure.repository.firmware.gridfs import GridFsFirmwareRepository
from ips_app.infrastructure.repository.node.beanie import BeanieNodeRepository
from ips_app.infrastructure.repository.node.beanie_model import NodeDocument
from ips_app.infrastructure.repository.node_network.beanie import (
    BeanieNodeNetworkRepository,
)
from ips_app.infrastructure.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)
from ips_app.infrastructure.repository.permission.beanie import (
    BeaniePermissionRepository,
)
from ips_app.infrastructure.repository.permission.beanie_model import (
    PermissionDocument,
)
from ips_app.infrastructure.repository.ranging.beanie import BeanieRangingRepository
from ips_app.infrastructure.repository.ranging.beanie_model import (
    RangingRecordDocument,
)
from ips_app.infrastructure.repository.ranging_scheduler_config.beanie import (
    BeanieRangingSchedulerConfigRepository,
)
from ips_app.infrastructure.repository.ranging_scheduler_config.beanie_model import (
    RangingSchedulerConfigDocument,
)
from ips_app.infrastructure.repository.role.beanie import BeanieRoleRepository
from ips_app.infrastructure.repository.role.beanie_model import RoleDocument
from ips_app.infrastructure.repository.user.beanie import BeanieUserRepository
from ips_app.infrastructure.repository.user.beanie_model import UserDocument
from ips_app.infrastructure.utility.namegen.random import RandomNameGenerator
from ips_app.infrastructure.utility.password.bcrypt import BcryptPasswordHasher
from ips_app.infrastructure.utility.token.jwt import JwtTokenIssuer
from ips_app.presentation.http.exception import register_exception_handlers
from ips_app.presentation.http.handlers.auth import AuthHandler
from ips_app.presentation.http.handlers.firmware import FirmwareHandler
from ips_app.presentation.http.handlers.node import NodeHandler
from ips_app.presentation.http.handlers.node_network import NodeNetworkHandler
from ips_app.presentation.http.handlers.permission import PermissionHandler
from ips_app.presentation.http.handlers.ranging import RangingHandler
from ips_app.presentation.http.handlers.ranging_scheduler_config import (
    RangingSchedulerConfigHandler,
)
from ips_app.presentation.http.handlers.role import RoleHandler
from ips_app.presentation.http.handlers.user import UserHandler
from ips_app.presentation.http.middlewares.auth_jwt import JwtMiddleware
from ips_app.presentation.http.routes import (
    auth,
    firmware,
    node,
    node_network,
    permission,
    ranging,
    ranging_scheduler_config,
    role,
    user,
)
from ips_app.presentation.task.handlers.ranging_scheduler import (
    RangingSchedulerHandler,
)
from ips_app.presentation.task.runners.ranging_scheduler import (
    create_runner as create_ranging_scheduler_runner,
)

DOCUMENT_MODELS = [
    PermissionDocument,
    RoleDocument,
    UserDocument,
    NodeNetworkDocument,
    NodeDocument,
    RangingRecordDocument,
    RangingSchedulerConfigDocument,
    FirmwareDocument,
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    motor = app.state.motor
    runner = app.state.ranging_scheduler_runner
    ranging_scheduler_config_repo = app.state.ranging_scheduler_config_repo

    await init_beanie(
        database=motor[env.APP_MONGO_DB],
        document_models=DOCUMENT_MODELS,
    )
    await ranging_scheduler_config_repo.load_cache()

    task = asyncio.create_task(runner(), name="ranging_scheduler")
    try:
        yield
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        motor.close()


def create_app() -> FastAPI:
    print(f"{app_config.APP_NAME} {app_config.APP_VERSION}")
    
    env.load_env()
    log = create_logger()
    motor = AsyncIOMotorClient(env.APP_MONGO_URI)

    repo_permission = BeaniePermissionRepository()
    repo_role = BeanieRoleRepository()
    repo_user = BeanieUserRepository()
    repo_node_network = BeanieNodeNetworkRepository()
    repo_node = BeanieNodeRepository()
    repo_ranging = BeanieRangingRepository()
    firmware_bucket = AsyncIOMotorGridFSBucket(motor[env.APP_MONGO_DB], bucket_name="firmware")
    repo_firmware = GridFsFirmwareRepository(firmware_bucket)
    repo_ranging_scheduler_config = BeanieRangingSchedulerConfigRepository(
        defaults=RangingSchedulerConfig(
            listen_timeout_uus=env.APP_RANGING_SCHEDULER_LISTEN_TIMEOUT_UUS,
            initiate_timeout_uus=env.APP_RANGING_SCHEDULER_INITIATE_TIMEOUT_UUS,
            listen_to_initiate_delay_ms=env.APP_RANGING_SCHEDULER_LISTEN_TO_INITIATE_DELAY_MS,
            pair_delay_ms=env.APP_RANGING_SCHEDULER_PAIR_DELAY_MS,
            idle_delay_ms=env.APP_RANGING_SCHEDULER_IDLE_DELAY_MS,
        )
    )

    node_control = WebSocketNodeControl()
    password_hasher = BcryptPasswordHasher()
    name_generator = RandomNameGenerator()
    token_issuer = JwtTokenIssuer(
        access_secret=env.APP_ACCESS_TOKEN_SECRET,
        access_expiry=env.APP_ACCESS_TOKEN_EXPIRY,
        refresh_secret=env.APP_REFRESH_TOKEN_SECRET,
        refresh_expiry=env.APP_REFRESH_TOKEN_EXPIRY,
    )

    permission_usecase = BasePermissionUsecase(repo_permission, log)
    role_usecase = BaseRoleUsecase(repo_role, log)
    user_usecase = BaseUserUsecase(repo_user, password_hasher, log)
    auth_usecase = BaseAuthUsecase(repo_user, password_hasher, token_issuer, log)
    node_network_usecase = BaseNodeNetworkUsecase(repo_node_network, log)
    node_usecase = BaseNodeUsecase(repo_node, node_control, log)
    node_connection_usecase = BaseNodeConnectionUsecase(
        repo_node, node_control, name_generator, log
    )
    ranging_usecase = BaseRangingUsecase(
        repo_ranging, repo_node, repo_node_network, log
    )
    ranging_scheduler_usecase = BaseRangingSchedulerUsecase(repo_node, node_control, log)
    firmware_usecase = BaseFirmwareUsecase(repo_firmware, repo_node, node_control, log)
    ranging_scheduler_config_usecase = BaseRangingSchedulerConfigUsecase(
        repo_ranging_scheduler_config, log
    )

    permission_handler = PermissionHandler(permission_usecase)
    role_handler = RoleHandler(role_usecase)
    user_handler = UserHandler(user_usecase)
    auth_handler = AuthHandler(auth_usecase, user_usecase)
    node_network_handler = NodeNetworkHandler(node_network_usecase)
    node_handler = NodeHandler(node_usecase, node_connection_usecase, ranging_usecase, log)
    ranging_handler = RangingHandler(ranging_usecase)
    ranging_scheduler_handler = RangingSchedulerHandler(ranging_scheduler_usecase, log)
    firmware_handler = FirmwareHandler(firmware_usecase)
    ranging_scheduler_config_handler = RangingSchedulerConfigHandler(
        ranging_scheduler_config_usecase
    )

    ranging_scheduler_runner = create_ranging_scheduler_runner(
        ranging_scheduler_handler,
        ranging_scheduler_config_usecase,
    )

    app = FastAPI(
        lifespan=lifespan,
        title=app_config.APP_NAME,
        version=app_config.APP_VERSION,
    )
    app.state.motor = motor
    app.state.ranging_scheduler_runner = ranging_scheduler_runner
    app.state.ranging_scheduler_config_repo = repo_ranging_scheduler_config

    register_exception_handlers(app)

    app.include_router(auth.create_router(auth_handler, role_usecase, log))
    app.include_router(user.create_router(user_handler, role_usecase, log))
    app.include_router(role.create_router(role_handler, role_usecase, log))
    app.include_router(permission.create_router(permission_handler, role_usecase, log))
    app.include_router(
        node_network.create_router(node_network_handler, role_usecase, log)
    )
    app.include_router(node.create_router(node_handler, role_usecase, log))
    app.include_router(ranging.create_router(ranging_handler, role_usecase, log))
    app.include_router(
        ranging_scheduler_config.create_router(
            ranging_scheduler_config_handler, role_usecase, log
        )
    )
    app.include_router(firmware.create_router(firmware_handler, role_usecase, log))

    app.add_middleware(
        JwtMiddleware,
        token_issuer=token_issuer,
        excluded_paths=[
            "/docs",
            "/docs/oauth2-redirect",
            "/redoc",
            "/openapi.json",
            "/auth/sign-in",
            "/auth/refresh-token",
            "/firmware/download",
        ],
    )

    return app


async def main() -> None:
    app = create_app()
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8000,
            access_log=False,
            log_level="warning",
        )
    )
    await server.serve()
