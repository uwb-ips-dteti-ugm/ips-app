# Project Overview: IPS App Backend

This backend is built with **Hexagonal Architecture (Ports and Adapters)** using **FastAPI**, **MongoDB**, **Motor**, and **Beanie ODM**. Business/application logic depends on ports and domain models. Framework and database details stay in controllers, compositions, and adapters.

## Directory Structure

- `src/ips_app/main.py`: ASGI entrypoint. Imports `create_app()` from `compositions/fastapi.py` and exposes `app`.
- `src/ips_app/compositions/fastapi.py`: FastAPI composition root. Loads config, creates the Mongo client, initializes Beanie, wires repositories, services, handlers, routes, and middleware.
- `src/ips_app/compositions/seeder.py`: Reserved for the seed composition entrypoint.
- `src/ips_app/config/`: Environment variable loading and default seed data.
- `src/ips_app/domain/models/`: Pure domain models and domain exceptions. These must not depend on Beanie, FastAPI, Motor, or controller DTOs.
- `src/ips_app/domain/ports/driving/`: Inbound interfaces, such as HTTP service contracts.
- `src/ips_app/domain/ports/driven/`: Outbound interfaces, such as repositories and logging.
- `src/ips_app/services/http/`: Business/application service implementations for HTTP driving ports.
- `src/ips_app/controllers/http/`: FastAPI-facing code: DTOs, handlers, middlewares, and route factories.
- `src/ips_app/adapters/repository/`: Beanie document models and repository adapter implementations.
- `src/ips_app/adapters/logging/`: Concrete logging adapter implementations.
- `src/ips_app/utils/`: Shared utilities for password hashing, JWT tokens, and validation.

## Application Flow

Startup begins in `src/ips_app/main.py`, which calls `create_app()` from `src/ips_app/compositions/fastapi.py`.

`create_app()` performs runtime wiring:

1. Loads environment variables from `config/env_var.py`.
2. Configures access-token and refresh-token settings.
3. Creates the selected logger implementation.
4. Creates a Motor `AsyncIOMotorClient`.
5. Initializes Beanie in the FastAPI lifespan with current document models.
6. Instantiates driven adapters, mainly Beanie repositories.
7. Instantiates HTTP services with repository and logging ports.
8. Instantiates HTTP handlers with driving service ports.
9. Includes FastAPI routers through each module's `create_router(...)` factory.
10. Adds `JwtMiddleware` as the outer request middleware and `ActivityUpdaterMiddleware` inside it.

A typical HTTP request flows through the system like this:

```text
HTTP request
 -> JwtMiddleware
 -> ActivityUpdaterMiddleware
 -> route dependencies, such as logger(...) and feature_guard(...)
 -> FastAPI route function
 -> HTTP handler
 -> HTTP service
 -> driven repository port
 -> Beanie repository adapter
 -> MongoDB
```

Example: `POST /auth/sign-in`

```text
routes/auth.py
 -> AuthHandler.post_sign_in()
 -> BaseAuthHTTP.sign_in()
 -> UserRepository.read_user_by_username()
 -> BeanieUserRepository
 -> UserDocument in the users collection
 -> user.password_auth password verification
 -> token generation
 -> TokenResponse
```

There is no separate auth repository or auth collection in the new app. Password auth is embedded in `User.auths`.

## Key Patterns & Conventions

### 1. Decoupled Models

Most persisted entities have two representations:

- **Domain model**: A pure Pydantic `BaseModel` in `domain/models/`, used by services and ports.
- **Document model**: A Beanie `Document` in `adapters/repository/*/beanie_model.py`, with MongoDB-specific settings, indexes, links, and a `to_domain()` method.

Do not put Beanie documents in the domain layer.

### 2. Ports and Adapters

- Driving ports define what the application can do from the outside, such as HTTP service operations.
- Driven ports define what the application needs from infrastructure, such as repositories and logging.
- HTTP services implement driving ports and depend on driven ports.
- HTTP handlers depend on driving ports, not concrete service classes.
- Beanie repositories implement driven repository ports.
- Repository and HTTP port class names do not use the `Port` suffix.

### 3. Controllers

- DTOs live in `controllers/http/dto/`.
- Handlers live in `controllers/http/handlers/`.
- Middlewares live in `controllers/http/middlewares/`.
- Route factories live in `controllers/http/routes/` and are named `create_router(...)`.
- Handlers translate domain results into DTOs and map domain exceptions to HTTP responses through `handlers/exception.py`.
- DTOs are HTTP transport shapes. Domain exceptions do not belong in DTO modules.

### 4. Auth & User

- Auth data is embedded on `User.auths`.
- `UserAuth` is a discriminated union so future auth methods can be added cleanly.
- Current supported auth type is password auth via `UserPasswordAuth`.
- Do not add a separate `AuthDocument`, auth repository, or auth MongoDB collection.
- Do not add an OAuth domain model until the product needs one.

### 5. Feature Access

- Feature CRUD belongs to `FeatureHTTP`.
- User feature access checks belong to `UserHTTP`, including `get_accessible_features(...)` and `can_access_feature_by_name(...)`.
- `feature_guard(...)` receives a `UserHTTP` service.
- Feature guard names use `/` separators, such as `user/manage`, `auth/manage`, and `feature/view`.

### 6. Logging

- **Tag format**: `ClassName.function_name` for classes, and action-specific route tags such as `UserRoutes.get_user`.
- Classes define `self.tag_class = "ClassName"` in `__init__`.
- Methods define `tag = f"{self.tag_class}.function_name"` and pass that tag to `log.info(...)` or `log.error(...)`.
- Route logger dependencies should be specific per route, with action-specific `2xx`, `4xx`, and `5xx` messages.

### 7. Error Handling

- Do not expose raw Python or library exceptions past adapters/services.
- Domain-level errors should use domain exceptions from `domain/models/exception.py`.
- Generic unexpected errors in adapters and services should be wrapped as `UnexpectedDomainException`.
- Handlers convert domain exceptions into HTTP responses.

### 8. Asynchronous I/O

All database, logging, repository, and service I/O is async and must be awaited.

### 9. Database & Transactions

- **ODM**: Beanie `1.26.0` as pinned in `requirements.txt`.
- **Mongo driver**: Motor `AsyncIOMotorClient`.
- **Beanie initialization**: Done in `compositions/fastapi.py` lifespan.
- **Document models**: `PermissionDocument`, `RoleDocument`, `UserDocument`, and `FeatureDocument`.
- **Transactions**: Managed at the service layer when a multi-document operation requires them. Services pass `session=session` to repositories through `**kwargs`.
- **Relationships**: Managed with Beanie `Link`. When only an ID is needed, prefer link reference IDs instead of fetching full documents.

### 10. API Naming Conventions

- Route factories are named `create_router(...)`.
- Handlers use the `httpverb_resource` pattern, such as `post_sign_in`, `patch_auth_me_password`, and `get_users`.
- Base service implementations are named with the `Base...HTTP` pattern, such as `BaseAuthHTTP`, `BaseUserHTTP`, and `BasePermissionHTTP`.
- Private helper methods should be placed at the bottom of adapter and service classes.

### 11. Dependency Injection

Dependencies are injected through constructors:

- Services take repository and logging ports.
- Handlers take service ports.
- Routes receive handlers, the `UserHTTP` service for guards, and loggers through `create_router(...)`.

Keep new modules consistent with this wiring style.

## Key Modules

- **Auth**: Username/password authentication, password hashing, JWT access/refresh tokens, sign-in, sign-up, sign-out, password changes, and embedded auth metadata updates.
- **User**: Profile data, preferences, role assignment, online/offline state, active/banned status, and feature access checks.
- **Role & Permission**: Granular access control. Roles link to permissions.
- **Feature**: Runtime access gates for API capabilities. Features link to permissions.
- **Composition**: Wires FastAPI, Beanie, repositories, services, handlers, routes, and middleware.
- **Seeder**: Creates base permissions, roles, feature gates, admin account, and test accounts. Seeder behavior lives in services; default seed data lives in `config/seed_data.py`.
