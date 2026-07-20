# IPS App — Indoor Positioning System

A UWB (ultra-wideband) indoor positioning system: ESP32 + DW3000 nodes perform two-way ranging with each other, a backend schedules those measurements and records the resulting distances, and a web dashboard is used to manage nodes and watch the results live. Built for DTETI UGM.

## How it fits together

```
Firmware (ESP32+DW3000)  <-- WiFi + WebSocket -->  Backend (FastAPI + MongoDB)  <-- HTTP/JSON -->  Frontend (Next.js)
```

- **[`firmware/`](./firmware)** — runs on each physical node. Connects to WiFi, opens a WebSocket to the backend, performs ranging on command, and can receive OTA firmware updates.
- **[`backend/`](./backend)** — the source of truth. Tracks registered nodes, schedules ranging between approved node pairs, stores results, hosts firmware binaries, and enforces role/permission-based access control over all of it.
- **[`frontend/`](./frontend)** — the admin/monitoring dashboard operators actually use: approve nodes, assign them to networks, watch ranging results in real time, manage users/roles, tune scheduler timing, and push firmware updates.

Each has its own README with setup/deployment/development instructions, and an `AGENTS.md` with the full architecture writeup for that part of the system.

## Features

- **Node lifecycle** — nodes self-register on first WebSocket connection (as `pending`); an admin assigns them to a network/PAN address and approves them before they're scheduled.
- **Automatic ranging** — a background scheduler cycles through every approved node pair on a network, running listen/initiate UWB exchanges with configurable timing (timeouts, inter-pair delay, idle backoff).
- **Live range monitor** — watch the latest distance for any node pair, updating in near real time.
- **OTA firmware updates** — build once, upload to the backend, push to every connected node over its existing WebSocket connection. The backend checks each node's reported board variant (flash size) against the uploaded binary before sending anything, so a node never gets flashed with an incompatible image.
- **Role-based access control** — users, roles, and fine-grained permissions (`<resource>/<view|manage|delete>`), enforced on every backend route and mirrored in what the frontend shows.
- **Resilient sessions** — short-lived access tokens are refreshed transparently in the background (frontend middleware), so long-running pages like the range monitor don't get randomly kicked out mid-session.

## Quick start

1. **Backend** — see [`backend/README.md`](./backend/README.md). `docker compose up -d --build` after copying `.env.example` to `.env`. This also creates the shared Docker network the frontend joins.
2. **Frontend** — see [`frontend/README.md`](./frontend/README.md). Start it after the backend; `docker compose up -d --build` after copying `.env.example` to `.env`.
3. **Firmware** — see [`firmware/README.md`](./firmware/README.md). Flash a board with PlatformIO, pointing it at the backend's WebSocket endpoint via `.env`, then approve it from the frontend's Nodes page.

## Tech stack

| Layer    | Stack |
| -------- | ----- |
| Firmware | C++ (Arduino framework), PlatformIO, ESP32, DW3000 |
| Backend  | Python, FastAPI, MongoDB (Beanie/Motor), JWT auth |
| Frontend | Next.js (App Router), React, TypeScript, Tailwind CSS |

All three follow the same clean-architecture layering (`domain` → `application`/`usecases` → `infrastructure` → `presentation` → `composition`), adapted to each language/runtime — see each subproject's `AGENTS.md` for the details.
