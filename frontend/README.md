# IPS App — Frontend

Next.js (App Router) admin/monitoring dashboard for the Indoor Positioning System: manage nodes, networks, users/roles/permissions, watch live ranging measurements, configure the ranging scheduler, and push OTA firmware updates to connected nodes. Talks to the [backend](../backend) over HTTP/JSON; the ESP32 nodes themselves never talk to this app directly.

## Requirements

- Node.js 24+ and npm (matches the Docker image; anything reasonably recent works for local dev)
- A running instance of the [backend](../backend) API

## Deployment / usage (Docker)

The backend's `docker-compose.yml` creates an external Docker network (`ips-app-network`) that this app's compose file joins — **start the backend first.**

```bash
# in backend/, if not already running:
docker compose up -d

# then in frontend/:
cp .env.example .env
# edit .env — IPS_API_BASE_URL must point at the backend as reachable from
# *inside* the Docker network (the default, http://backend:8000, works if both
# compose files are on the same host)

docker compose up -d --build
```

Served on `${PORT_FRONTEND:-3000}` (host) → `3000` (container). Sign in with a backend-seeded account (see `backend/README.md`).

To stop: `docker compose down`.

## Development

```bash
npm install
IPS_API_BASE_URL=http://localhost:50002 npm run dev   # point at wherever the backend is actually reachable
```

Open `http://localhost:3000`. Type-check and lint before committing:

```bash
npx tsc --noEmit
npm run lint
```

## Structure

- `src/app/(app)/sign-in` — the public sign-in page.
- `src/app/(dashboard)` — everything behind auth, gated by `(dashboard)/layout.tsx`. Grouped into `admin/*` (users, roles, permissions, firmware, settings) and `node/*` (nodes, networks, range monitor). Each leaf route follows the same shape: `page.tsx` (Server Component, loads data) + `_lib/get-*-page-data.ts` (permission checks + data fetching) + `_actions/*.ts` (`"use server"` mutations) + `_components/*.tsx`.
- `src/lib/api/` — one thin module per backend resource (`node.ts`, `firmware.ts`, `user.ts`, ...), all built on `client.ts`'s `requestJson`/`ApiError`. Adding a new backend endpoint means adding a function here, not reinventing fetch logic per page.
- `src/lib/auth/` — cookie-based session handling (`session.ts`, `cookies.ts`, `token.ts`). Access/refresh JWTs are stored as `httpOnly` cookies; only `getAuthSession()`/Server Actions ever see the raw access token.
- `src/proxy.ts` — Next.js's request-interception layer (the renamed `middleware.ts`, see the note below). Proactively refreshes an expired access token (using the refresh-token cookie) before every page load, `router.refresh()`, and Server Action call, and redirects to `/sign-in` (with `callbackUrl`) if the refresh token is also gone. This is why sessions don't randomly "break" mid-use even though access tokens are short-lived — don't remove or bypass it.
- `src/shared/` — design-system building blocks (`components/Table.tsx`, `Modal.tsx`, `FormControls.tsx`, `ErrorToast.tsx`, ...) and shared icons, reused across every feature page instead of one-off UI per page.

> **Next.js 16 renamed `middleware.ts` to `proxy.ts`** — same mechanism, same file location (`src/`), just a new name. If you're looking for auth/redirect interception logic, that's the file.

## Notes

- All backend calls happen server-side (Server Components/Server Actions) — the browser never holds a bearer token directly.
- Permission checks are re-derived per page (`getMyPermissions()` + a `Set<string>` of granted names) rather than trusted from a client-side cache; the sidebar (`src/app/_components/Sidebar.tsx` + `DashboardShell.tsx`) filters visible menu items the same way.
- No test suite exists yet; rely on `tsc`/`eslint` plus manual verification against a running backend.
