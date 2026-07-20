# Project Overview: IPS App Backend

IPS App is an indoor positioning system backend: it registers UWB (ultra-wideband) nodes over a websocket connection, schedules ranging measurements between node pairs, records the resulting distances, and exposes all of it through an HTTP API with role/permission-based access control.

This backend is being rewritten from a hexagonal ("ports and adapters") design into **Clean Architecture**, built with **FastAPI**, **MongoDB**, **Motor**, and **Beanie ODM**. The rewrite lives under `src/`. The previous hexagonal implementation is preserved read-only under `_src/` purely as a migration reference — do not add new features there, and do not import from it.

The dependency rule: inner layers (`domain`) never import outer layers (`application`, `infrastructure`, `presentation`, `composition`). Outer layers depend inward through abstract contracts, never the reverse.

## Directory Structure (`src/ips_app/`)

Layers, from innermost to outermost:

- **`domain/models/`** — Pure Pydantic `BaseModel`s and domain exceptions. Zero dependency on Beanie, FastAPI, Motor, or DTOs. One file per entity (`user.py`, `role.py`, `permission.py`, `node.py`, `node_network.py`, `ranging.py`, `ranging_scheduler_config.py`, `logger.py`), plus `exception.py` for the `DomainException` hierarchy.
- **`domain/contracts/`** — Abstract base classes (ABCs) that outer layers implement, grouped by capability:
  - `repository/` — one ABC per persisted entity (`permission.py`, `role.py`, `user.py`, `node.py`, `node_network.py`, `ranging.py`, `ranging_scheduler_config.py`).
  - `logger/leveled.py` — `LeveledLogger` (async `error`/`warn`/`info`/`debug`).
  - `node/control.py` — `NodeControl`, the abstraction over a live node connection (register/unregister, restart, ranging listen/initiate).
  - `utility/` — `password.py` (hashing), `token.py` (JWT issuing/validation), `namegen.py` (random display-name generation for auto-registered nodes).
- **`domain/usecases/`** — ABCs describing what the application can do, one per entity/concern (`auth.py`, `permission.py`, `role.py`, `user.py`, `node.py`, `node_connection.py`, `node_network.py`, `ranging.py`, `ranging_scheduler.py`, `ranging_scheduler_config.py`). Grouped by **capability**, not by driver type (there is no separate "HTTP usecase" vs "cron usecase" split like the old `services/http` vs `services/cron`).
- **`application/<entity>/<entity>.py`** — Concrete `Base<Entity>Usecase` implementations of the usecase ABCs above. Depend only on `domain/contracts` ABCs (repository, logger, control, utility), never on a concrete infrastructure class.
- **`infrastructure/`** — Concrete adapters implementing `domain/contracts`:
  - `repository/<entity>/beanie.py` + `beanie_model.py` — Beanie `Document` model and the repository implementation, one pair per entity.
  - `repository/_shared/` — cross-repository helpers: `object_id.py` (string→`PydanticObjectId` coercion), `pagination.py` (`paginate`/`paginate_with_links`), `link.py` (Beanie `Link` resolution helpers — see "Beanie Links" below), `duplicate.py` (extract offending fields from a `DuplicateKeyError`).
  - `node/control/websocket.py` — `WebSocketNodeControl`, the live implementation of `NodeControl` backed by an in-memory `Dict[device_id, WebSocket]` guarded by an `asyncio.Lock`.
  - `logger/leveled/{basic,json}.py` — plain-text and JSON `LeveledLogger` implementations.
  - `utility/{password/bcrypt.py, token/jwt.py, namegen/random.py}` — bcrypt hashing, PyJWT issuing/validation, random name generation.
- **`presentation/`** — Framework-facing code, split by driver:
  - `http/dto/` — Pydantic request/response models. Requests use `ConfigDict(extra="forbid")`; responses extend `AuditedResponse` (`created_at/created_by/updated_at/updated_by`) with a `from_domain(...)` classmethod.
  - `http/handlers/` — thin pass-throughs: unwrap a DTO, call the usecase, wrap the result back into a response DTO. No try/except, no logging — that's handled centrally (see below).
  - `http/routes/` — one `create_router(handler, role_usecase, log) -> APIRouter` factory per entity. Builds `permission_check([...], role_usecase)` guards and attaches a `logger(log, "<Entity>Routes/<fn>")` dependency to every route.
  - `http/middlewares/` — `auth_jwt.py` (`JwtMiddleware` + `get_claims()`), `permission_check.py` (`authorization_check`/`permission_check` route guards), `logger.py` (per-request structured access logging).
  - `http/exception.py` — `register_exception_handlers(app)`, the single place that maps every `DomainException` subclass to an HTTP status code.
  - `task/handlers/` and `task/runners/` — the ranging-scheduler background task (see "Ranging Scheduler" below). There is no separate cron/APScheduler layer; the task loop is a plain `asyncio` coroutine created by `create_runner(...)` and run via `asyncio.create_task(...)` in the app's `lifespan`.
  - **Websockets are merged into the owning entity's HTTP router**, not a separate `presentation/websocket/` package — `/nodes/ws/{device_id}` is registered inside `presentation/http/routes/node.py` alongside the node's REST routes, and handled by the same `NodeHandler`.
- **`composition/`** — Dependency-injection wiring (the "composition root"):
  - `main/launcher.py` — `create_app() -> FastAPI` (wires every repo → usecase → handler → router, registers middleware, builds the scheduler task runner) and `async def main()` (builds the app and self-hosts it via `uvicorn.Server(...).serve()`).
  - `seeder/launcher.py` — `async def main()` for the one-shot seeding process; composes existing usecases (no dedicated "seeder usecases") plus `composition/seeder/{permission,role,user}.py` orchestration helpers.
  - `_shared/logger.py` — `create_logger()`, shared between both launchers to avoid duplicating the `APP_LOGGER_FORMAT` branch.
- **`config/`** — `env.py` (env var loading with typed getters: `get_string`/`get_int`/`get_duration_seconds`/`get_logger_format`/`get_logger_level`), `app.py` (`APP_NAME`, `APP_VERSION`), `seed_data.py` (`SEED_PERMISSIONS`, `SEED_ROLES`, `build_seed_users(...)`).
- **`main.py`** — the single process entrypoint (see "Entrypoint Dispatcher" below).

## Entrypoint Dispatcher

There is no module-level `app = create_app()` for a CLI-invoked `uvicorn module:app` anymore. `main.py` is a small `argparse`-based dispatcher with one positional `mode` arg (`"main"` or `"seeder"`, default `"main"`) that imports and runs the matching launcher's `async def main()` via `asyncio.run(...)`:

```text
python -m ips_app.main            # -> composition/main/launcher.py:main()   (the API server)
python -m ips_app.main seeder     # -> composition/seeder/launcher.py:main() (one-shot seed, then exit)
```

Launchers themselves have no `if __name__ == "__main__"` — they are only ever invoked through this dispatcher. `Dockerfile`'s `CMD` and `docker-compose.yml`'s `seeder` service `command` both go through `python -m ips_app.main <mode>`. Uvicorn is self-hosted programmatically (`uvicorn.Server(uvicorn.Config(app, ...)).serve()`) inside `main()` rather than invoked from the CLI, because there is no importable module-level `app` object to point a CLI `uvicorn` command at.

## Application Flow

Startup: `main.py` → `composition/main/launcher.py:main()` → `create_app()`.

`create_app()` performs synchronous wiring:

1. `env.load_env()`, then `create_logger()`.
2. Creates the Motor `AsyncIOMotorClient`.
3. Instantiates every Beanie repository (stateless, zero-arg — see "Repositories are stateless" below, with the ranging-scheduler-config repository as the one deliberate exception).
4. Instantiates infrastructure singletons: `WebSocketNodeControl`, `BcryptPasswordHasher`, `RandomNameGenerator`, `JwtTokenIssuer` (built from the token env vars).
5. Instantiates every `Base<Entity>Usecase` with its repo(s) + logger (+ control/hasher/name-generator where relevant).
6. Instantiates every HTTP handler with its usecase(s).
7. Builds the ranging-scheduler task runner via `create_runner(handler, config_usecase)`.
8. Builds `FastAPI(lifespan=lifespan, title=app_config.APP_NAME, version=app_config.APP_VERSION)`, stashes `motor`/`ranging_scheduler_runner`/`ranging_scheduler_config_repo` on `app.state` for the `lifespan` context manager to reach.
9. `register_exception_handlers(app)`.
10. `app.include_router(...)` for every entity (node's router includes its `/ws/{device_id}` endpoint).
11. `app.add_middleware(JwtMiddleware, token_issuer=..., excluded_paths=[...])` — added last, so it ends up outermost (Starlette applies middleware in reverse-registration order). `BaseHTTPMiddleware` never sees websocket scopes, so JWT auth for the node websocket is enforced inside the domain usecase (`NodeConnectionUsecase.register_connection`), not this middleware.

The FastAPI `lifespan` (module-level `async def lifespan(app)`, not nested inside `create_app()`) then, on startup: `await init_beanie(document_models=DOCUMENT_MODELS)`, `await ranging_scheduler_config_repo.load_cache()` (populate the in-memory config cache — see below), then `asyncio.create_task(runner(), name="ranging_scheduler")`. On shutdown: cancel that task, `await asyncio.gather(task, return_exceptions=True)`, `motor.close()`.

A typical HTTP request flows:

```text
HTTP request
 -> JwtMiddleware (validates bearer token, sets a ContextVar with UserAccessTokenClaims)
 -> route dependencies: logger(log, "<Entity>Routes/<fn>") + permission_check([...], role_usecase)
 -> FastAPI route function
 -> HTTP handler (DTO -> usecase call -> DTO)
 -> usecase (validate -> repo/control call -> log -> re-raise/wrap as DomainException)
 -> repository (Beanie Document <-> domain model translation, DB-specific errors -> DomainException)
 -> MongoDB
```

Any `DomainException` raised anywhere unwinds straight to `register_exception_handlers`, which maps it to the right status code — handlers themselves never catch exceptions.

## Key Patterns & Conventions

### 1. Decoupled models

Every persisted entity has two representations: a pure Pydantic domain model in `domain/models/` (used by usecases and contracts), and a Beanie `Document` in `infrastructure/repository/<entity>/beanie_model.py` (Mongo-specific: `class Settings: name = "<collection>"`, indexes, `Link` fields) with a `to_domain()` method mapping 1:1 onto the domain model. Never put a Beanie `Document` in `domain/`.

### 2. Repositories are stateless (with one deliberate exception)

Every repository is instantiated with zero constructor args (`BeanieUserRepository()`) and holds no instance state — all error translation (`DuplicateKeyError` → `DuplicateDomainException`, missing doc → `NotFoundDomainException`) happens inline in each method. **The one exception is `BeanieRangingSchedulerConfigRepository`**, which holds an in-memory cache + `asyncio.Lock` (see "Ranging Scheduler Config" below) — the same shape `WebSocketNodeControl` already uses for its live connection dict. If a future repository needs similar runtime-mutable state, follow that same pattern rather than inventing a new one.

### 3. Usecase skeleton

Every `Base<Entity>Usecase` method follows the same shape:

```python
async def some_method(self, ...) -> SomeModel:
    tag = f"{self.tag_class}/some_method"
    try:
        # validate via application/_shared/validator.py helpers
        result = await self.repo.some_repo_method(...)
        await self.log.info(tag, "Successfully did the thing", {...meta})
        return result
    except Exception as e:
        await self.log.error(tag, "Failed to do the thing", {"error": str(e), ...meta})
        if isinstance(e, DomainException):
            raise
        raise UnexpectedDomainException(str(e)) from e
```

`self.tag_class = self.__class__.__name__` is set once in `__init__`. Constructors take `(repo, log)` plus any additional contracts the usecase needs (`control`, `password_hasher`, `name_generator`, `token_issuer`) — always ending in `log`.

### 4. Validation

Shared validators live in `application/_shared/validator.py`: `validate_name`, `validate_resource_name`, `validate_username`, `validate_password`, `validate_description`, `validate_bio`, `validate_non_empty_string`, `validate_ids_list`, `validate_preferences`, `validate_positive_integer`, `validate_non_negative_float`, `validate_uwb_value`, `validate_node_network_assignment`, `validate_record_interval`. Reuse these before adding a new one.

### 5. Presentation layer

- DTOs: request models use `ConfigDict(extra="forbid")`; response models extend `AuditedResponse` and provide `from_domain(cls, model) -> Response`.
- Handlers are thin pass-throughs — no try/except, no logging.
- Routes: `create_router(handler, role_usecase, log) -> APIRouter`. Build one `permission_check([...], role_usecase)` guard per action tier (`guard_manage`, `guard_view`, `guard_delete` — omit tiers that don't apply, e.g. a singleton config has no delete). Every route gets `dependencies=[logger(log, "<Entity>Routes/<fn>"), guard_x]`.
- Action-style, non-CRUD operations are their own `POST` sub-route rather than a flag on an existing verb — e.g. `POST /nodes/{device_id}/restart`, `POST /ranging-scheduler-config/reset`. Prefer this over overloading `PATCH` with a boolean "mode" field.
- Permission names use `"<kebab-resource>/<action>"` (e.g. `node-network/manage`, `ranging-scheduler-config/view`); add new ones to `config/seed_data.py:SEED_PERMISSIONS` and, if the admin role should have it, nowhere else — the admin role's `permission_names` is derived from the full `SEED_PERMISSIONS` list automatically.

### 6. Auth & User

`User.password_hash` is a plain field directly on the domain model — there is no `UserAuth` discriminated union or embedded auth-methods list like the old codebase. Add a new auth method by extending `User` directly if/when the product needs one; don't reintroduce the old union pattern speculatively.

### 7. Node lifecycle & websocket

A node has a `NodeStatus` (`pending` → `approved`/`suspended`). Connecting over `/nodes/ws/{device_id}` auto-registers a `pending` node if it doesn't exist yet (via `NodeConnectionUsecase._create_node_registration_if_missing`, using `RandomNameGenerator` for a display name), but `register_connection` rejects any node that isn't `approved` with `ForbiddenDomainException`. The handler (`presentation/http/handlers/node.py:connect_node_websocket`) catches `DomainException` and closes the socket with `WS_1008_POLICY_VIOLATION`, and unexpected exceptions with `WS_1011_INTERNAL_ERROR` — the websocket lifecycle is entirely handled inside the merged HTTP handler, not a separate presentation module.

### 8. Ranging & the ranging scheduler

`RangingPair` (in-memory: network + listener node + initiator node + `cycle_done`) is distinct from `RangingRecord` (persisted: same shape plus `distance` and `recorded_at`). The scheduler task (`presentation/task/runners/ranging_scheduler.py:create_runner`) loops: refresh registered nodes → get next pair → listen → initiate → sleep, driven by `presentation/task/handlers/ranging_scheduler.py:RangingSchedulerHandler` and `domain/usecases/ranging_scheduler.py:RangingSchedulerUsecase` (node pairing/timing logic — distinct from `ranging_scheduler_config`, which is just the tunable numbers).

### 9. Ranging scheduler config (cached singleton entity)

The 5 scheduler timing knobs (`listen_timeout_uus`, `initiate_timeout_uus`, `listen_to_initiate_delay_ms`, `pair_delay_ms`, `idle_delay_ms`) are a DB-backed singleton, runtime-updatable via `GET`/`PATCH`/`POST .../reset` on `/ranging-scheduler-config`, not baked into the task runner's closure at startup:

- `env.APP_RANGING_SCHEDULER_*` are the **deploy-time defaults only** — passed into `BeanieRangingSchedulerConfigRepository(defaults=...)` at construction.
- `repo.load_cache()` get-or-creates the one DB document and populates an in-memory cache; called once at startup by both the seeder (to guarantee the doc exists before the API ever starts) and the main app's `lifespan` (to populate the cache before the scheduler task starts reading it).
- `repo.get_cached_config()` serves reads with no DB round-trip; `repo.update_config(...)`/`repo.reset_config_to_default(...)` write the DB doc and refresh the cache, guarded by the repo's own `asyncio.Lock`.
- The task runner calls `await config_usecase.get_config()` **every loop iteration** instead of closing over fixed ints — a `PATCH`/reset takes effect on the very next cycle, no restart needed.
- This is the template to follow for any other future "tunable knob that needs to change without a restart" — put the cache in the repository (not the usecase), keep the usecase a fully conventional thin wrapper, and have whatever reads it live (a task runner, a handler) re-fetch on each use rather than capturing a value once.

### 10. Error handling

`domain/models/exception.py` defines the full `DomainException` hierarchy (`NotFoundDomainException`, `DuplicateDomainException`, `ValidatorDomainException`, `ForbiddenDomainException`, `NodeNotConnectedDomainException`, `InvalidCredentialsDomainException`, `InvalidTokenDomainException`, `ExpiredTokenDomainException`, `UnexpectedDomainException`). `presentation/http/exception.py:EXCEPTION_STATUS_MAP` is the single source of truth mapping each to a status code (400/401/403/404/409/500) — extend that map, don't add per-route exception handling. Adapters/usecases wrap any non-domain exception as `UnexpectedDomainException(str(e))`.

### 11. Logging

Tag format is `ClassName/method_name` (slash, not dot). Classes set `self.tag_class = self.__class__.__name__` once in `__init__`; methods build `tag = f"{self.tag_class}/method_name"`. Route-level access logging is automatic via the `logger(log, "<Entity>Routes/<fn>")` dependency (`presentation/http/middlewares/logger.py`), which logs `info`/`warn`/`error` based on the resulting status code — individual route functions never log directly.

### 12. Asynchronous I/O

Every usecase, repository, and contract method is `async def` and awaited — including trivial in-memory reads (e.g. `RangingSchedulerConfigRepository.get_cached_config`) — for interface uniformity across the whole call chain, not just where I/O is actually happening.

### 13. Database

- ODM: Beanie `1.26.0`; driver: Motor `AsyncIOMotorClient` (see `requirements.txt` for exact pins).
- `init_beanie(document_models=DOCUMENT_MODELS)` runs once, in `composition/main/launcher.py`'s `lifespan`, and separately (with a subset of the same Document classes) in the seeder's `main()`.
- **Beanie Links**: fetching a `Link` field eagerly (`fetch_links=True`) rewrites simple queries into an aggregation pipeline that resolves links *before* `$match` runs, so filtering on a linked doc's nested id (e.g. `"network.$id"`) silently fails to match. Work around it with the two-phase pattern in `infrastructure/repository/_shared/link.py:find_one_with_links` (locate the id unresolved first, then re-`get()` with `fetch_links=True`), and use `required_link`/`resolved_link`/`resolved_links` to safely unwrap a `Link[T] | T` field that's expected to already be resolved.
- Transactions: pass `session=session` through repository methods when a multi-document operation needs one.

### 14. API naming

- Route factories: `create_router(handler, role_usecase, log) -> APIRouter`.
- Route/handler functions: `<httpverb>_<resource>[_<subresource>]`, e.g. `post_sign_in`, `patch_node_status`, `get_ranging_scheduler_config`, `post_ranging_scheduler_config_reset`.
- Concrete usecase implementations: `Base<Entity>Usecase` (e.g. `BaseAuthUsecase`, `BaseRangingSchedulerConfigUsecase`).
- Repository/contract class names do not use a `Port`/`Contract` suffix.

### 15. Dependency injection

Constructor injection only, wired exclusively in `composition/main/launcher.py` and `composition/seeder/launcher.py`:

- Usecases take repo(s)/control/utility contracts + `log`.
- Handlers take usecase(s) (+ `log` where the handler itself needs to log, e.g. websocket lifecycle events).
- Routes take `(handler, role_usecase, log)` via `create_router(...)`.
- Task runners take `(handler, config_usecase)` via `create_runner(...)`.

Keep any new module consistent with this wiring style — do not construct a repository, control, or utility instance anywhere outside a `composition/*/launcher.py`.

## Key Modules

- **Auth**: username/password sign-in, JWT access/refresh tokens (`JwtTokenIssuer`), bcrypt hashing.
- **User**: profile, preferences, `UserStatus` (active/suspended/banned), role assignment.
- **Role & Permission**: roles embed their full list of `Permission` objects; `permission_check([...], role_usecase)` is the enforcement point.
- **Node & Node Network**: a `Node` optionally belongs to a `NodeNetwork` (PAN id + address assignment); `NodeStatus` gates websocket registration.
- **Ranging & Ranging Scheduler**: pairs approved, network-assigned nodes for listen/initiate ranging cycles and persists the resulting `RangingRecord`s.
- **Ranging Scheduler Config**: the cached, runtime-updatable singleton described above.
- **Composition**: `main/launcher.py` (API server) and `seeder/launcher.py` (one-shot bootstrap), both reached through `main.py`'s mode dispatcher.
- **Seeder**: idempotent (`*_exists_by_name` checks before creating) — seeds `SEED_PERMISSIONS`, `SEED_ROLES` (admin gets every seeded permission automatically, `user` gets none), the admin/test user accounts, and the ranging-scheduler-config singleton document, all from `config/seed_data.py` + `config/env.py` values. No dedicated "seeder usecases" — it composes the same usecases the API uses.

## Migration Notes (`_src/` → `src/`)

`_src/` is the old hexagonal-architecture implementation, kept only as a reference during the rewrite — treat it as read-only, do not extend it. As of this writing:

- Every `ips_app` layer has a verified, feature-complete equivalent under `src/` (domain models, contracts, usecases, applications, infrastructure adapters, HTTP + websocket presentation, the ranging-scheduler task, the seeder, and the main composition), plus one net-new capability with no old equivalent: the cached ranging-scheduler-config entity.
- **`_src/ips_dummy_node/`** (a standalone UWB-node simulator — connects over the raw node websocket protocol, no import of `ips_app` internals) has **not** been migrated or copied anywhere under `src/`. It still works against the new backend as-is (the websocket protocol is unchanged), but if `_src/` is ever deleted, move `ips_dummy_node/` out first or it will be lost from the working tree.
