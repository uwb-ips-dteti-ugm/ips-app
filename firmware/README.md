# IPS App — Firmware

ESP32 + DW3000 (UWB) firmware for a ranging node. Connects to WiFi, opens a WebSocket to the [backend](../backend)'s `/nodes/ws/{device_id}`, waits for ranging/restart/OTA commands, performs stateless single-sided UWB ranging, and reports results back. Built with PlatformIO / Arduino framework.

See [`AGENTS.md`](./AGENTS.md) for the full architecture writeup (clean-architecture layering, WebSocket command reference, domain value types, conventions for adding a new feature).

## Requirements

- [PlatformIO](https://platformio.org/) (CLI or the VS Code extension — `.vscode/` is already configured)
- An ESP32 dev board wired to a DW3000 UWB module (SPI: reset=GPIO27, IRQ=GPIO34, CS=GPIO4 — see `include/config/config.h`; use `lib/DW3000/examples/` as the wiring/setup reference)
- A running [backend](../backend) reachable from the board's network

## Deployment / usage

```bash
cp .env.example .env
# edit .env: WIFI_SSID, WIFI_PASSWORD, UWB_SERVER_SCHEME/HOST/PORT/PATH
# (UWB_SERVER_PATH must be /nodes/ws — that's the backend's actual mounted route)

pio run -e esp32dev-8mb -t upload    # or esp32dev-16mb — match the board's actual flash size
pio device monitor -e esp32dev-8mb   # Serial monitor; prints firmware version + board variant at boot
```

Check the board's actual flash size first if unsure:

```bash
python -m esptool --chip esp32 --port /dev/ttyUSB0 flash_id
```

The two PlatformIO environments (`esp32dev-8mb`/`esp32dev-16mb`) use different partition tables (`partitions/8MB.csv`/`16MB.csv`) — flashing the wrong one can corrupt the partition layout. Both partition tables are already OTA-ready (dual `ota_0`/`ota_1` app partitions).

A freshly-connected node shows up on the backend as `pending` — approve it (and assign it a network/address) from the frontend's Nodes page before it can be used.

### OTA updates

No CI/CD — after building, upload the binary + version metadata to the backend manually, then push it to connected nodes from the frontend's Firmware page:

```bash
python3 -m pip install -r scripts/requirements.txt
cp scripts/upload_firmware.config.example.json scripts/upload_firmware.config.json
# edit upload_firmware.config.json: version, backend_url, board_variant, username, password
python3 scripts/upload_firmware.py
```

The backend refuses to push firmware to a node whose reported board variant doesn't match the uploaded binary's — this is why the board variant is baked into the firmware itself (`platformio.ini`'s `${PIOENV}` build flag) and reported on every WebSocket connect.

## Development

```bash
pio run -e esp32dev-8mb -e esp32dev-16mb   # build both environments — do this after every change
```

Bump `UWB_FIRMWARE_VERSION` in `platformio.ini`'s shared `[env]` section on every release (and keep it in sync with the `version` you upload via `upload_firmware.config.json`) — it's printed as the first line on Serial at boot, which makes it easy to confirm exactly what's flashed on a given board.

Code layout mirrors the backend's clean architecture, adapted to embedded C++: `domain/models` (value types, framework-free) → `domain/contracts` (interfaces infrastructure implements) → `domain/usecases` (interfaces presentation calls) → `application` (usecase implementations) → `infrastructure` (concrete adapters: WiFi, DW3000, WebSocket, OTA) → `presentation/task` (FreeRTOS task controllers) → `composition` (the composition root, `App`, owns every concrete object) → `config` (compile-time constants from `.env`/`platformio.ini`). Full details and the "adding a new feature" checklist are in [`AGENTS.md`](./AGENTS.md).

### Testing without hardware

`scripts/uwb_server_test.py` is a standalone FastAPI server speaking the same `/nodes/ws/{device_id}` protocol as the real backend — useful for exercising firmware changes (or writing a fake node for backend testing) without a physical board:

```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/uwb_server_test.py
```

`scripts/check_node_ws.py` is a small CLI for checking whether a given `ws://`/`wss://` node URL is accepted or rejected by a running backend — handy for diagnosing connectivity/approval issues without flashing anything:

```bash
python3 scripts/check_node_ws.py ws://<backend-host>:<port>/nodes/ws/<device_id>
```

## Notes

- `.env` is gitignored but its values get compiled directly into the firmware binary — don't commit real WiFi credentials or point `.env.example` at anything real.
- `lib/DW3000` (and the unused `lib/DW1000`) are local vendored libraries — treat `lib/DW3000/examples/` as the source of truth for low-level radio setup, not the internet.
