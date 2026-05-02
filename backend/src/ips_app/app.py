from contextlib import asynccontextmanager
from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from ips_app.config.env_var import load_env_var
from ips_app.domain.models.logging import LogLevel
from ips_app.utils.token import config_access_token, config_refresh_token

# driven — logging
from ips_app.adapters.driven.logging.generic.basic import BasicGenericLogging
from ips_app.adapters.driven.logging.generic.json import JSONGenericLogging

# driven — repositories
from ips_app.adapters.driven.repository.auth.beanie import BeanieAuthRepository
from ips_app.adapters.driven.repository.user.beanie import BeanieUserRepository
from ips_app.adapters.driven.repository.role.beanie import BeanieRoleRepository
from ips_app.adapters.driven.repository.permission.beanie import BeaniePermissionRepository
from ips_app.adapters.driven.repository.feature.beanie import BeanieFeatureRepository

# driven — beanie documents (needed for init_beanie)
from ips_app.adapters.driven.repository.permission.beanie_model import PermissionDocument
from ips_app.adapters.driven.repository.role.beanie_model import RoleDocument
from ips_app.adapters.driven.repository.user.beanie_model import UserDocument
from ips_app.adapters.driven.repository.auth.beanie_model import AuthDocument
from ips_app.adapters.driven.repository.feature.beanie_model import FeatureDocument

# domain services
from ips_app.domain.services.http.auth.base import AuthHTTPService
from ips_app.domain.services.http.user.base import UserHTTPService
from ips_app.domain.services.http.role.base import RoleHTTPService
from ips_app.domain.services.http.permission.base import PermissionHTTPService
from ips_app.domain.services.http.feature.base import FeatureHTTPService

# driving — handlers
from ips_app.adapters.driving.http.handler.auth import AuthHandler
from ips_app.adapters.driving.http.handler.user import UserHandler
from ips_app.adapters.driving.http.handler.role import RoleHandler
from ips_app.adapters.driving.http.handler.permission import PermissionHandler
from ips_app.adapters.driving.http.handler.feature import FeatureHandler

# driving — routes
from ips_app.adapters.driving.http.routes import auth, user, role, permission, feature

# driving — middleware
from ips_app.adapters.driving.http.middleware.auth_jwt import JwtMiddleware


def create_app() -> FastAPI:
    env_var = load_env_var()

    config_access_token(env_var.access_token_secret, env_var.access_token_expiry)
    config_refresh_token(env_var.refresh_token_secret, env_var.refresh_token_expiry)

    log_level = LogLevel[env_var.log_level]
    log = JSONGenericLogging(log_level) if env_var.log_style == "json" else BasicGenericLogging(log_level)

    motor = AsyncIOMotorClient(env_var.mongo_uri)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await init_beanie(
            database=motor[env_var.mongo_db],  # type: ignore[arg-type]
            document_models=[
                PermissionDocument,
                RoleDocument,
                UserDocument,
                AuthDocument,
                FeatureDocument,
            ],
        )
        yield
        motor.close()

    app = FastAPI(lifespan=lifespan)

    # repositories
    repo_auth = BeanieAuthRepository(log)
    repo_user = BeanieUserRepository(log)
    repo_role = BeanieRoleRepository(log)
    repo_perm = BeaniePermissionRepository(log)
    repo_feat = BeanieFeatureRepository(log)

    # services
    auth_service = AuthHTTPService(motor, repo_auth, repo_user, repo_role, log)
    user_service = UserHTTPService(repo_user, log)
    role_service = RoleHTTPService(repo_role, log)
    perm_service = PermissionHTTPService(repo_perm, log)
    feat_service = FeatureHTTPService(repo_feat, repo_user, repo_role, log)

    # handlers
    auth_handler = AuthHandler(auth_service)
    user_handler = UserHandler(user_service)
    role_handler = RoleHandler(role_service)
    perm_handler = PermissionHandler(perm_service)
    feat_handler = FeatureHandler(feat_service)

    # routers
    app.include_router(auth.create_router(auth_handler, feat_service, log))
    app.include_router(user.create_router(user_handler, feat_service, log))
    app.include_router(role.create_router(role_handler, feat_service, log))
    app.include_router(permission.create_router(perm_handler, feat_service, log))
    app.include_router(feature.create_router(feat_handler, feat_service, log))

    # middleware — added last, runs outermost (first on request)
    app.add_middleware(
        JwtMiddleware,
        excluded_paths=[
            "/auth/sign-up",
            "/auth/sign-in",
            "/auth/refresh-token",
        ],
    )

    return app
