# Project Overview: IPS App Backend

This backend is built using **Hexagonal Architecture (Ports and Adapters)** with **FastAPI** and **MongoDB (Beanie ODM)**. It emphasizes decoupling business logic from infrastructure.

## Directory Structure

- `src/ips_app/domain/models/`: Pure domain entities (Pydantic `BaseModel`) and Beanie Documents (`Document`).
- `src/ips_app/domain/services/`: Business logic implementations that fulfill driving ports.
- `src/ips_app/ports/driving/`: Inward-facing interfaces (e.g., HTTP Service interfaces).
- `src/ips_app/ports/driven/`: Outward-facing interfaces (e.g., Repository, Logging).
- `src/ips_app/adapters/driving/`: Entry point implementations (FastAPI Handlers, DTOs, Middlewares, Routes).
- `src/ips_app/adapters/driven/`: Infrastructure implementations (Beanie Repositories, specific Loggers).
- `src/ips_app/utils/`: Shared utilities (Password hashing, JWT, Validators).

## Key Patterns & Conventions

### 1. Decoupled Models
Every entity has two representations in the domain layer:
- **Domain Model**: A pure Pydantic `BaseModel` used for business logic.
- **Document Model**: A Beanie `Document` with MongoDB-specific configurations (indexes, etc.). It includes a `to_domain()` method.

### 2. Logging
- **Tag Format**: `ClassName.function_name`.
- **Implementation**: Classes define `self.tag_class = "ClassName"` in `__init__`. Methods define `tag = f"{self.tag_class}.function_name"` for use in `log.info/error` calls.

### 3. Asynchronous everything
All I/O operations (database, logging, services) are `async` and must be awaited.

### 4. Database & Transactions
- **ODM**: Beanie 2.x.
- **Transactions**: Managed at the **Service Layer** using the Motor `AsyncIOMotorClient`. Sessions are passed to repository methods via `**kwargs`.
- **Relationships**: Managed using Beanie `Link`. Access IDs using `link.ref.id` to avoid unnecessary database fetches.

### 5. API Naming Conventions
- **Handlers**: Methods follow the `httpverb_resource` pattern (e.g., `post_user`, `patch_role_preferences`, `get_user_me`).
- **Feature Guards**: Feature names use `/` as a separator (e.g., `user/manage`, `auth/view`).

### 6. Dependency Injection
Dependencies are injected via constructors (Services take Repository ports; Handlers take Service ports). In FastAPI routes, use the `create_router` factory pattern to wire these dependencies.

## Key Modules
- **Auth**: Username-based authentication, JWT tokens, and password management.
- **User**: Profile management, state (online/offline), and status (active/banned).
- **Role & Permission**: Granular access control. Roles contain lists of permission links.
- **Feature**: Access gates for specific system functionalities, mapped to permissions.
