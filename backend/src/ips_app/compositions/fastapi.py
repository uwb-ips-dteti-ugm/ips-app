import asyncio
from contextlib import asynccontextmanager
from typing import Any, Callable, Coroutine, cast

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from ips_app.adapters.control.node.websocket import WebSocketNodeControl
from ips_app.adapters.logging.leveled.basic import BasicLeveledLogging
from ips_app.adapters.logging.leveled.json import JSONLeveledLogging
from ips_app.adapters.repository.node.beanie import BeanieNodeRepository
from ips_app.adapters.repository.node.beanie_model import NodeDocument
from ips_app.adapters.repository.node_network.beanie import BeanieNodeNetworkRepository
from ips_app.adapters.repository.node_network.beanie_model import NodeNetworkDocument
from ips_app.adapters.repository.permission.beanie import BeaniePermissionRepository
from ips_app.adapters.repository.permission.beanie_model import PermissionDocument
from ips_app.adapters.repository.record.beanie import BeanieRecordRepository
from ips_app.adapters.repository.record.beanie_model import RecordDocument
from ips_app.adapters.repository.role.beanie import BeanieRoleRepository
from ips_app.adapters.repository.role.beanie_model import RoleDocument
from ips_app.adapters.repository.user.beanie import BeanieUserRepository
from ips_app.adapters.repository.user.beanie_model import UserDocument
from ips_app.config.env_var import EnvVar, load_env_var
from ips_app.controllers.http.handlers.auth import AuthHandler
from ips_app.controllers.http.handlers.node import NodeHandler
from ips_app.controllers.http.handlers.node_network import NodeNetworkHandler
from ips_app.controllers.http.handlers.permission import PermissionHandler
from ips_app.controllers.http.handlers.record import RecordHandler
from ips_app.controllers.http.handlers.role import RoleHandler
from ips_app.controllers.http.handlers.user import UserHandler
from ips_app.controllers.http.middlewares.auth_jwt import JwtMiddleware
from ips_app.controllers.http.routes import (
    auth,
    node,
    node_network,
    permission,
    record,
    role,
    user,
)
from ips_app.controllers.task.handlers.ranging_scheduler import (
    RangingSchedulerTaskHandler,
)
from ips_app.controllers.task.runners.ranging_scheduler import (
    create_runner as create_ranging_scheduler_runner,
)
from ips_app.domain.models.exception import ValidatorDomainException
from ips_app.domain.models.log import LogLevel
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.services.http.auth.base import BaseAuthHTTP
from ips_app.services.http.node.base import BaseNodeHTTP
from ips_app.services.http.node_network.base import BaseNodeNetworkHTTP
from ips_app.services.http.permission.base import BasePermissionHTTP
from ips_app.services.http.record.base import BaseRecordHTTP
from ips_app.services.http.role.base import BaseRoleHTTP
from ips_app.services.http.user.base import BaseUserHTTP
from ips_app.services.task.ranging_scheduler.base import BaseRangingSchedulerTask
from ips_app.utils.token import config_access_token, config_refresh_token
from ips_app.utils.validator import validate_positive_integer


TaskRunner = tuple[str, Callable[[], Coroutine[Any, Any, None]]]


@asynccontextmanager
async def lifespan(app: FastAPI):
    env_var = cast(EnvVar, app.state.env_var)
    motor = cast(AsyncIOMotorClient, app.state.motor)
    task_runners = cast(list[TaskRunner], app.state.task_runners)

    await init_beanie(
        database=motor[env_var.mongo_db],  # type: ignore[arg-type]
        document_models=[
            PermissionDocument,
            RoleDocument,
            UserDocument,
            NodeNetworkDocument,
            NodeDocument,
            RecordDocument,
        ],
    )

    task_handles = _start_task_runners(task_runners)
    try:
        yield
    finally:
        await _stop_task_runners(task_handles)
        motor.close()


def create_app() -> FastAPI:
    env_var = load_env_var()
    _validate_ranging_scheduler_env(env_var)
    _config_tokens(env_var)

    log = _create_logger(env_var)
    motor = AsyncIOMotorClient(env_var.mongo_uri)
    task_runners: list[TaskRunner] = []

    app = FastAPI(
        lifespan=lifespan,
        title="IPS App API",
        version="1.0.0",
    )

    repo_permission = BeaniePermissionRepository(log)
    repo_role = BeanieRoleRepository(log)
    repo_user = BeanieUserRepository(log)
    repo_node_network = BeanieNodeNetworkRepository(log)
    repo_node = BeanieNodeRepository(log)
    repo_record = BeanieRecordRepository(log)
    node_control = WebSocketNodeControl(log)

    permission_service = BasePermissionHTTP(repo_permission, log)
    role_service = BaseRoleHTTP(repo_role, log)
    user_service = BaseUserHTTP(repo_user, log)
    auth_service = BaseAuthHTTP(repo_user, log)
    node_network_service = BaseNodeNetworkHTTP(repo_node_network, log)
    node_service = BaseNodeHTTP(
        repo=repo_node,
        repo_node_network=repo_node_network,
        repo_record=repo_record,
        control=node_control,
        log=log,
    )
    record_service = BaseRecordHTTP(repo_record, log)
    ranging_scheduler_service = BaseRangingSchedulerTask(
        repo_node=repo_node,
        control=node_control,
        log=log,
    )

    permission_handler = PermissionHandler(permission_service)
    role_handler = RoleHandler(role_service)
    user_handler = UserHandler(user_service)
    auth_handler = AuthHandler(auth_service)
    node_network_handler = NodeNetworkHandler(node_network_service)
    node_handler = NodeHandler(node_service, log)
    record_handler = RecordHandler(record_service)
    ranging_scheduler_handler = RangingSchedulerTaskHandler(
        service=ranging_scheduler_service,
        log=log,
    )
    task_runners.append(
        (
            "ranging_scheduler",
            create_ranging_scheduler_runner(
                handler=ranging_scheduler_handler,
                listen_timeout_uus=env_var.ranging_scheduler_listen_timeout_uus,
                initiate_timeout_uus=(
                    env_var.ranging_scheduler_initiate_timeout_uus
                ),
                listen_to_initiate_delay_ms=(
                    env_var.ranging_scheduler_listen_to_initiate_delay_ms
                ),
                pair_delay_ms=env_var.ranging_scheduler_pair_delay_ms,
                idle_delay_ms=env_var.ranging_scheduler_idle_delay_ms,
            ),
        )
    )

    app.state.env_var = env_var
    app.state.motor = motor
    app.state.task_runners = task_runners

    app.include_router(auth.create_router(auth_handler, role_service, log))
    app.include_router(user.create_router(user_handler, role_service, log))
    app.include_router(role.create_router(role_handler, role_service, log))
    app.include_router(permission.create_router(permission_handler, role_service, log))
    app.include_router(
        node_network.create_router(node_network_handler, role_service, log)
    )
    app.include_router(node.create_router(node_handler, role_service, log))
    app.include_router(record.create_router(record_handler, role_service, log))

    app.add_middleware(
        JwtMiddleware,
        excluded_paths=[
            "/docs",
            "/docs/oauth2-redirect",
            "/redoc",
            "/openapi.json",
            "/auth/sign-in",
            "/auth/refresh-token",
        ],
    )

    return app


def _config_tokens(env_var: EnvVar) -> None:
    config_access_token(env_var.access_token_secret, env_var.access_token_expiry)
    config_refresh_token(env_var.refresh_token_secret, env_var.refresh_token_expiry)


def _validate_ranging_scheduler_env(env_var: EnvVar) -> None:
    validate_positive_integer(
        env_var.ranging_scheduler_listen_timeout_uus,
        "RANGING_SCHEDULER_LISTEN_TIMEOUT_UUS",
    )
    validate_positive_integer(
        env_var.ranging_scheduler_initiate_timeout_uus,
        "RANGING_SCHEDULER_INITIATE_TIMEOUT_UUS",
    )
    validate_positive_integer(
        env_var.ranging_scheduler_listen_to_initiate_delay_ms,
        "RANGING_SCHEDULER_LISTEN_TO_INITIATE_DELAY_MS",
    )
    validate_positive_integer(
        env_var.ranging_scheduler_pair_delay_ms,
        "RANGING_SCHEDULER_PAIR_DELAY_MS",
    )
    validate_positive_integer(
        env_var.ranging_scheduler_idle_delay_ms,
        "RANGING_SCHEDULER_IDLE_DELAY_MS",
    )


def _start_task_runners(
    task_runners: list[TaskRunner],
) -> list[asyncio.Task[None]]:
    return [
        asyncio.create_task(runner(), name=name)
        for name, runner in task_runners
    ]


async def _stop_task_runners(
    task_handles: list[asyncio.Task[None]],
) -> None:
    for task in task_handles:
        task.cancel()

    if task_handles:
        await asyncio.gather(*task_handles, return_exceptions=True)


def _create_logger(env_var: EnvVar) -> LeveledLogging:
    try:
        log_level = LogLevel[env_var.log_level]
    except KeyError as e:
        raise ValidatorDomainException(
            "LOG_LEVEL must be one of NONE, ERROR, WARN, INFO, or DEBUG."
        ) from e

    if env_var.log_style == "json":
        return JSONLeveledLogging(log_level)
    if env_var.log_style == "basic":
        return BasicLeveledLogging(log_level)

    raise ValidatorDomainException("LOG_FORMAT must be either 'basic' or 'json'.")
