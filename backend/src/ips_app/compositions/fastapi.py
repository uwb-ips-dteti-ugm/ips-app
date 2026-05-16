import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Awaitable, Callable, cast

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from beanie import init_beanie
from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient

from ips_app.adapters.logging.generic.basic import BasicGenericLogging
from ips_app.adapters.logging.generic.json import JSONGenericLogging
from ips_app.adapters.node.control.websocket import WebSocketNodeControl
from ips_app.adapters.repository.feature.beanie import BeanieFeatureRepository
from ips_app.adapters.repository.feature.beanie_model import FeatureDocument
from ips_app.adapters.repository.node.beanie import BeanieNodeRepository
from ips_app.adapters.repository.node.beanie_model import NodeDocument
from ips_app.adapters.repository.permission.beanie import BeaniePermissionRepository
from ips_app.adapters.repository.permission.beanie_model import PermissionDocument
from ips_app.adapters.repository.record.beanie import BeanieRecordRepository
from ips_app.adapters.repository.record.beanie_model import RecordDocument
from ips_app.adapters.repository.role.beanie import BeanieRoleRepository
from ips_app.adapters.repository.role.beanie_model import RoleDocument
from ips_app.adapters.repository.user.beanie import BeanieUserRepository
from ips_app.adapters.repository.user.beanie_model import UserDocument
from ips_app.config.env_var import EnvVar, load_env_var
from ips_app.controllers.cron.handlers.user_state_updater import (
    UserStateUpdaterCronHandler,
)
from ips_app.controllers.cron.jobs.user_state_updater import (
    create_job as create_user_state_updater_job,
)
from ips_app.controllers.http.handlers.auth import AuthHandler
from ips_app.controllers.http.handlers.feature import FeatureHandler
from ips_app.controllers.http.handlers.node import NodeHandler
from ips_app.controllers.http.handlers.permission import PermissionHandler
from ips_app.controllers.http.handlers.record import RecordHandler
from ips_app.controllers.http.handlers.role import RoleHandler
from ips_app.controllers.http.handlers.user import UserHandler
from ips_app.controllers.http.middlewares.activity_updater import ActivityUpdaterMiddleware
from ips_app.controllers.http.middlewares.auth_jwt import JwtMiddleware
from ips_app.controllers.http.routes import (
    auth,
    feature,
    node,
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
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.services.cron.user_state_updater.base import BaseUserStateUpdaterCron
from ips_app.services.http.auth.base import BaseAuthHTTP
from ips_app.services.http.feature.base import BaseFeatureHTTP
from ips_app.services.http.node.base import BaseNodeHTTP
from ips_app.services.http.permission.base import BasePermissionHTTP
from ips_app.services.http.record.base import BaseRecordHTTP
from ips_app.services.http.role.base import BaseRoleHTTP
from ips_app.services.http.user.base import BaseUserHTTP
from ips_app.services.task.ranging_scheduler.base import BaseRangingSchedulerTask
from ips_app.utils.token import config_access_token, config_refresh_token
from ips_app.utils.validator import validate_cron_period, validate_positive_integer


CronJob = tuple[str, Callable[[], Awaitable[None]], int]
TaskRunner = tuple[str, Callable[[], Awaitable[None]]]


@asynccontextmanager
async def lifespan(app: FastAPI):
    env_var = cast(EnvVar, app.state.env_var)
    motor = cast(AsyncIOMotorClient, app.state.motor)
    cron_jobs = cast(list[CronJob], app.state.cron_jobs)
    task_runners = cast(list[TaskRunner], app.state.task_runners)

    await init_beanie(
        database=motor[env_var.mongo_db],  # type: ignore[arg-type]
        document_models=[
            PermissionDocument,
            RoleDocument,
            UserDocument,
            FeatureDocument,
            NodeDocument,
            RecordDocument,
        ],
    )

    await _run_cron_jobs_at_init(cron_jobs)
    scheduler = AsyncIOScheduler(timezone="UTC")
    _schedule_cron_jobs(scheduler, cron_jobs)
    scheduler.start()
    task_handles = _start_task_runners(task_runners)
    try:
        yield
    finally:
        await _stop_task_runners(task_handles)
        if scheduler.running:
            scheduler.shutdown(wait=False)
        motor.close()


def create_app() -> FastAPI:
    env_var = load_env_var()
    validate_cron_period(env_var.user_state_updater_cron_period)
    validate_positive_integer(
        env_var.ranging_scheduler_sleep_ms,
        "RANGING_SCHEDULER_SLEEP_MS",
    )
    validate_positive_integer(
        env_var.ranging_scheduler_listen_for_ms,
        "RANGING_SCHEDULER_LISTEN_FOR_MS",
    )
    validate_positive_integer(
        env_var.ranging_scheduler_wait_for_ms,
        "RANGING_SCHEDULER_WAIT_FOR_MS",
    )

    _config_tokens(env_var)

    log = _create_logger(env_var)
    motor = AsyncIOMotorClient(env_var.mongo_uri)
    security_scheme = HTTPBearer(auto_error=False)
    cron_jobs: list[CronJob] = []
    task_runners: list[TaskRunner] = []

    app = FastAPI(
        lifespan=lifespan,
        title="IPS App API",
        version="1.0.0",
        dependencies=[Depends(security_scheme)],
    )

    repo_permission = BeaniePermissionRepository(log)
    repo_role = BeanieRoleRepository(log)
    repo_user = BeanieUserRepository(log)
    repo_feature = BeanieFeatureRepository(log)
    repo_node = BeanieNodeRepository(log)
    repo_record = BeanieRecordRepository(log)
    node_control = WebSocketNodeControl(log)

    permission_service = BasePermissionHTTP(repo_permission, log)
    role_service = BaseRoleHTTP(repo_role, log)
    feature_service = BaseFeatureHTTP(repo_feature, log)
    user_service = BaseUserHTTP(
        repo=repo_user,
        repo_feature=repo_feature,
        repo_role=repo_role,
        log=log,
    )
    auth_service = BaseAuthHTTP(
        repo_user=repo_user,
        repo_role=repo_role,
        log=log,
    )
    node_service = BaseNodeHTTP(
        repo=repo_node,
        repo_record=repo_record,
        control=node_control,
        log=log,
    )
    record_service = BaseRecordHTTP(
        repo=repo_record,
        log=log,
    )
    user_state_updater_service = BaseUserStateUpdaterCron(
        repo_user=repo_user,
        log=log,
        away_after_seconds=env_var.user_state_to_away_after,
        offline_after_seconds=env_var.user_state_to_offline_after,
    )
    ranging_scheduler_service = BaseRangingSchedulerTask(
        repo_node=repo_node,
        control=node_control,
        log=log,
    )

    permission_handler = PermissionHandler(permission_service)
    role_handler = RoleHandler(role_service)
    feature_handler = FeatureHandler(feature_service)
    user_handler = UserHandler(user_service)
    auth_handler = AuthHandler(auth_service)
    node_handler = NodeHandler(node_service)
    record_handler = RecordHandler(record_service)
    user_state_updater_handler = UserStateUpdaterCronHandler(
        service=user_state_updater_service,
        log=log,
    )
    ranging_scheduler_handler = RangingSchedulerTaskHandler(
        service=ranging_scheduler_service,
        log=log,
    )
    cron_jobs.append(
        (
            "user_state_updater",
            create_user_state_updater_job(user_state_updater_handler),
            env_var.user_state_updater_cron_period,
        )
    )
    task_runners.append(
        (
            "ranging_scheduler",
            create_ranging_scheduler_runner(
                handler=ranging_scheduler_handler,
                sleep_ms=env_var.ranging_scheduler_sleep_ms,
                listen_for_ms=env_var.ranging_scheduler_listen_for_ms,
                wait_for_ms=env_var.ranging_scheduler_wait_for_ms,
            ),
        )
    )

    app.state.env_var = env_var
    app.state.motor = motor
    app.state.cron_jobs = cron_jobs
    app.state.task_runners = task_runners

    app.include_router(auth.create_router(auth_handler, user_service, log))
    app.include_router(user.create_router(user_handler, user_service, log))
    app.include_router(role.create_router(role_handler, user_service, log))
    app.include_router(permission.create_router(permission_handler, user_service, log))
    app.include_router(feature.create_router(feature_handler, user_service, log))
    app.include_router(node.create_router(node_handler, user_service, log))
    app.include_router(record.create_router(record_handler, user_service, log))

    jwt_excluded_paths = [
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
        "/openapi.json",
        "/auth/sign-up",
        "/auth/sign-in",
        "/auth/refresh-token",
    ]
    activity_updater_excluded_paths = [
        *jwt_excluded_paths,
        "/auth/sign-out",
    ]
    app.add_middleware(
        ActivityUpdaterMiddleware,
        user_service=user_service,
        excluded_paths=activity_updater_excluded_paths,
    )
    app.add_middleware(
        JwtMiddleware,
        excluded_paths=jwt_excluded_paths,
    )

    return app


def _config_tokens(env_var: EnvVar) -> None:
    config_access_token(env_var.access_token_secret, env_var.access_token_expiry)
    config_refresh_token(env_var.refresh_token_secret, env_var.refresh_token_expiry)


def _schedule_cron_jobs(
    scheduler: AsyncIOScheduler,
    cron_jobs: list[CronJob],
) -> None:
    now = datetime.now(timezone.utc)
    for name, job, period_seconds in cron_jobs:
        scheduler.add_job(
            job,
            trigger="interval",
            seconds=period_seconds,
            id=name,
            name=name,
            coalesce=True,
            max_instances=1,
            next_run_time=now + timedelta(seconds=period_seconds),
        )


async def _run_cron_jobs_at_init(
    cron_jobs: list[CronJob],
) -> None:
    for _, job, _ in cron_jobs:
        await job()


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


def _create_logger(env_var: EnvVar) -> GenericLogging:
    try:
        log_level = LogLevel[env_var.log_level]
    except KeyError as e:
        raise ValidatorDomainException(
            "LOG_LEVEL must be one of NONE, ERROR, WARN, INFO, or DEBUG."
        ) from e

    if env_var.log_style == "json":
        return JSONGenericLogging(log_level)
    if env_var.log_style == "basic":
        return BasicGenericLogging(log_level)

    raise ValidatorDomainException("LOG_FORMAT must be either 'basic' or 'json'.")
