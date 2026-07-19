# Environment & Setup

This file is not itself a checklist section — it documents the shared deployment, fixtures, and conventions every other `scenarios/*.md` file assumes. Read this first.

## Deploying the app

From `backend/`:

```bash
docker compose up -d --build
```

This builds and starts four services: `mongo` (replica-set-enabled MongoDB), `mongo-init` (one-shot replica-set initializer), `seeder` (one-shot, seeds permissions/roles/users/ranging-scheduler-config then exits), `backend` (the API server, waits for `seeder` to complete successfully before starting).

- **Base URL** (REST): `http://localhost:50002` — from `.env`'s `DOCKER_PORT_BACKEND=50002`, mapped to the container's internal port `8000` (`APP_PORT`).
- **Websocket base**: `ws://localhost:50002`.
- **Mongo** is reachable at `localhost:50003` (`DOCKER_PORT_MONGO`) if a test needs a direct driver connection instead of `mongosh` inside the container.

Confirm everything is up before running any scenario:

```bash
docker compose ps
docker compose logs seeder        # should show permission/role/user seed lines and exit 0
curl -s http://localhost:50002/openapi.json | head -c 200   # confirms the API is answering
```

## Seeded accounts

From `.env` (`APP_SEEDER_*`) + `src/ips_app/config/seed_data.py`:

| Username | Password | Role | Permissions |
|---|---|---|---|
| `admin` | `CHANGE_ME` | `admin` | all 21 seeded permissions (see below) |
| `user` | `CHANGE_ME` | `user` | none (`is_default=True`) |

Seeded permissions (`SEED_PERMISSIONS`, all granted to `admin`, none to `user`): `auth/manage`, `permission/manage`, `permission/view`, `permission/delete`, `role/manage`, `role/view`, `role/delete`, `user/manage`, `user/view`, `user/delete`, `node-network/manage`, `node-network/view`, `node-network/delete`, `node/manage`, `node/view`, `node/delete`, `ranging/manage`, `ranging/view`, `ranging/delete`, `ranging-scheduler-config/manage`, `ranging-scheduler-config/view`.

Get a fresh admin token:

```bash
ADMIN_TOKEN=$(curl -s -X POST http://localhost:50002/auth/sign-in \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"CHANGE_ME"}' | jq -r .access_token)
```

Same pattern for the plain `user` account (used for permission-negative scenarios) with `USER_TOKEN`.

## Token expiry caveat — sign in fresh, don't reuse tokens across scenarios

`.env` sets `APP_ACCESS_TOKEN_EXPIRY=1m` — **access tokens expire after 60 seconds**. Every scenario below assumes you sign in immediately before running it (or shortly before, within the same 60s window) rather than reusing a token captured much earlier in a long test session. This short expiry is also exactly what makes `AUTH-07` (expired-token scenario) realistic without mocking time: sign in, `sleep 65`, then use the token and expect `401`.

If you need a longer-lived token for a long manual session, use `POST /auth/refresh-token` to mint a new access token instead of re-signing-in, or temporarily bump `APP_ACCESS_TOKEN_EXPIRY` in `.env` and `docker compose up -d --build` again (not part of the default checklist run — note it if you do this, since it changes `AUTH-07`'s timing).

## Resetting state between runs

Full clean reseed (drops all data including the Mongo volume):

```bash
docker compose down -v
docker compose up -d --build
```

Non-destructive single-collection wipe (faster, useful between re-runs of one scenario file — collection names are the Mongo collection, not the API path, e.g. `permissions`, `roles`, `users`, `node_networks`, `nodes`, `ranging_records`, `ranging_scheduler_config`):

```bash
docker exec ips-app-mongo mongosh -u mongouser -p mongopass --authenticationDatabase admin \
  --eval "db.getSiblingDB('ips-app').nodes.deleteMany({})"
```

Re-running the seeder alone (idempotent — safe to run again on an existing DB, will not duplicate seeded permissions/roles/users or reset the ranging-scheduler-config singleton since it already exists):

```bash
docker compose run --rm seeder
```

## Direct Mongo inspection

For assertions curl can't make (e.g. confirming a password hash actually changed, confirming `updated_by` was stamped correctly, or counting documents):

```bash
docker exec ips-app-mongo mongosh -u mongouser -p mongopass --authenticationDatabase admin \
  --eval "db.getSiblingDB('ips-app').users.find({username:'admin'}).pretty()"
```

## Logs

```bash
docker compose logs -f backend    # structured JSON per request (presentation/http/middlewares/logger.py)
docker compose logs -f seeder     # one-shot, exits after seeding — check this first if fixtures seem missing
docker compose logs -f mongo
```

## Conventions used throughout `scenarios/*.md`

- `$ADMIN_TOKEN` / `$USER_TOKEN` — freshly-obtained bearer tokens (see above).
- `$FOO_ID` — an id captured from a prior scenario's response, typically via `| jq -r .id`.
- Every scenario states its **Preconditions** and is written to be runnable given those preconditions — it does not strictly require running the entire file top-to-bottom, but related scenarios within a file (e.g. create → get → update → delete) are ordered so earlier scenarios naturally satisfy later ones' preconditions.
- Every curl snippet uses `-s -w '\n%{http_code}'` so the last line of output is the HTTP status code and everything above it is the response body — makes it trivial to assert both body and status from a single command.
- IDs referenced across files (e.g. a node-network created in `07_node_network.md` used by `08_ranging.md`) are called out explicitly in that scenario's **Preconditions** line.
