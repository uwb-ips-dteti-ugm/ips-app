# IPS App — Backend

FastAPI backend for the Indoor Positioning System. Registers UWB nodes over a WebSocket, schedules ranging measurements between node pairs, records the results, serves OTA firmware to nodes, and exposes all of it through an HTTP API with role/permission-based access control. Data is stored in MongoDB via Beanie/Motor.

See [`AGENTS.md`](./AGENTS.md) for the full architecture writeup (clean-architecture layering, request flow, conventions for adding a new feature).

## Requirements

- Docker + Docker Compose (recommended), or Python 3.12 + a reachable MongoDB replica set for running it bare
- MongoDB must run as a replica set (Beanie/Motor transactions require it) — the bundled `docker-compose.yml` sets this up automatically

## Deployment / usage (Docker)

```bash
cp .env.example .env
# edit .env — at minimum change the CHANGE_ME secrets/passwords, and set
# APP_PUBLIC_BASE_URL to the host/port nodes will reach this backend on

docker compose up -d --build
```

This starts, in order: `mongo` (replica set + healthcheck) → `mongo-init` (one-shot replica set initiation) → `seeder` (one-shot: seeds permissions/roles/admin+default user, see below) → `backend` (the API server).

The API is published on `${DOCKER_PORT_BACKEND:-50002}` (host) → `8000` (container). Interactive docs at `http://localhost:50002/docs`.

Default seeded accounts (override via `.env` before first run):

| Role  | Username | Password (`.env`)             |
| ----- | -------- | ------------------------------ |
| admin | `admin`  | `APP_SEEDER_ADMIN_PASSWORD`    |
| user  | `user`   | `APP_SEEDER_USER_PASSWORD`     |

The seeder only *adds* permissions/roles/users that don't already exist by name — it never overwrites or removes. If you pull an update that adds new permissions to an existing deployment, re-run the seeder (`docker compose up seeder`) and then manually grant the new permissions to any existing custom roles (the built-in `admin` role only gets newly-seeded permissions automatically if it's a *newly created* role — on an existing DB you must assign them yourself via the Roles page/API).

To stop: `docker compose down` (add `-v` to also drop the Mongo volume).

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # point APP_MONGO_URI at a reachable replica-set Mongo,
                        # e.g. run just `docker compose up -d mongo mongo-init` for that

python -m ips_app.main seeder   # one-shot: seed permissions/roles/default users
python -m ips_app.main          # run the API server on :8000 (fixed port, self-hosted via uvicorn)
```

There is no `uvicorn module:app` entrypoint — the server is self-hosted programmatically inside `composition/main/launcher.py:main()`. Everything goes through `python -m ips_app.main [main|seeder]`.

Code layout (`src/ips_app/`): `domain` (models/contracts/usecases, framework-free) → `application` (usecase implementations) → `infrastructure` (Beanie repositories, WebSocket node control, JWT/bcrypt) → `presentation` (HTTP DTOs/handlers/routes, the ranging-scheduler background task) → `composition` (dependency wiring, one launcher per entrypoint mode). Full details, conventions, and "how to add a feature" steps are in [`AGENTS.md`](./AGENTS.md).

`docs/agent_tests/` contains per-version, per-endpoint API test scenarios (plain markdown, request/response walkthroughs) — useful as both living documentation and a manual/agent-driven regression checklist when changing a route.

## Configuration reference

All configuration is environment variables, loaded from `.env` (see `.env.example` for the full list with defaults):

- **Mongo**: `APP_MONGO_URI`, `APP_MONGO_DB`
- **Public URL**: `APP_PUBLIC_BASE_URL` — must be reachable by ESP32 nodes over plain HTTP (used to build firmware download links)
- **Tokens**: `APP_ACCESS_TOKEN_SECRET`/`_EXPIRY`, `APP_REFRESH_TOKEN_SECRET`/`_EXPIRY` (durations like `1m`, `7d`)
- **Seeder**: `APP_SEEDER_ADMIN_*`, `APP_SEEDER_USER_*`
- **Ranging scheduler defaults**: `APP_RANGING_SCHEDULER_*` (timeouts/delays in µs/ms — overridable at runtime via the Settings page once seeded)
- **Logger**: `APP_LOGGER_FORMAT` (`plain`/`json`), `APP_LOGGER_LEVEL` (`error`/`warn`/`info`/`debug`)

## Testing a node without hardware

The firmware repo ships `firmware/scripts/uwb_server_test.py`, a standalone fake-node/dev-server script useful for exercising this backend's `/nodes/ws/{device_id}` protocol without a physical board — see [`../firmware/AGENTS.md`](../firmware/AGENTS.md).
