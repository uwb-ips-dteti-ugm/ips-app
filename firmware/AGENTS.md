# AGENTS.md

## Project Idea

This repository contains ESP32 firmware for a UWB ranging device built around a DW3000 radio. The device keeps WiFi connected, connects to the backend's node WebSocket over `/nodes/ws/{device_id}`, waits for ranging commands, performs stateless single-sided UWB ranging, and reports either the ranging result or an error back to the server.

The firmware follows the same clean-architecture layering as the backend (`backend/src/ips_app`), adapted to embedded C++:

- `domain/models`: shared value types and protocol/frame constants, framework-independent.
- `domain/contracts`: interfaces implemented by infrastructure (Arduino, DW3000, WiFi, WebSocket libraries) — the C++ analogue of the backend's `domain/contracts` repository interfaces.
- `domain/usecases`: interfaces presentation calls into — the C++ analogue of the backend's `domain/usecases`.
- `application`: concrete usecase implementations. Application depends on domain contracts/usecases, not concrete infrastructure.
- `infrastructure`: concrete adapters implementing domain contracts against real libraries (Serial, ESP32 WiFi, DW3000, arduinoWebSockets).
- `presentation`: runtime presenters — currently FreeRTOS task controllers that translate task ticks and WebSocket events into calls on `application`.
- `composition`: the composition root. Owns concrete objects, initializes hardware, wires dependencies, and starts the application.
- `config`: compile-time configuration constants, populated from a local `.env` at build time.

The DW3000 infrastructure intentionally does not initialize the DW3000 chip. DW3000 setup belongs in the composition layer.

## Purpose

The main runtime flow is:

1. Arduino `setup()` creates `composition::App` and calls `run()`.
2. `App::setup()` initializes `Serial`, SPI, and the DW3000 chip, then validates required runtime configuration (WiFi SSID, UWB server host/port) and halts on failure.
3. `App::initControllers()` starts the FreeRTOS task controllers (`presentation::task::WiFiConnection`, `presentation::task::UWBStateless`).
4. The WiFi task keeps the ESP32 connected indefinitely.
5. The UWB stateless task connects to the WebSocket server at `/nodes/ws/<device_id>`, handles commands, runs ranging, and sends results.
6. `App::run()` ends in an infinite delay, so Arduino `loop()` is intentionally unused.

All concrete dependencies (adapters, application implementations, controllers) are constructed once, in `App`'s constructor initializer list — that construction step is the composition root's dependency-injection point, equivalent to how the backend's `composition/main` wires concrete repositories/usecases/handlers via constructor arguments. There is no separate "initialize infrastructure/services" phase — everything is either constructed there or, for hardware bring-up that can't happen in a constructor (SPI, the DW3000 chip), performed in `App::setup()`.

## Structure

Important directories:

- `include/domain/models`: `models::RangingCommand`, `models::RangingResult`, `models::RangingFailure` (the ranging command/result/failure value types — see "Domain Value Types" below), `models::Error`, and UWB frame-layout constants (`RangingFrameControl`, `RangingFunctionCode`, `RangingFrameLength`, `RangingFrameIndex`).
- `include/domain/contracts`: infrastructure-facing interfaces implemented by `infrastructure/`.
- `include/domain/usecases`: application-facing interfaces used by `presentation/`.
- `include/application` and `src/application`: usecase implementations. Application depends on `domain/contracts`/`domain/usecases`, not concrete infrastructure.
- `include/infrastructure` and `src/infrastructure`: concrete implementations for Serial logging, ESP32 WiFi, DW3000 ranging, and the arduinoWebSockets client.
- `include/presentation` and `src/presentation`: runtime presenters. Current presenters are FreeRTOS task controllers (`presentation/task`).
- `include/composition` and `src/composition`: composition root, hardware setup, object wiring.
- `include/config`: compile-time configuration constants.
- `scripts/load_env.py`: PlatformIO pre-script that loads local `.env` values into compile-time macros.
- `scripts/uwb_server_test.py`: a standalone FastAPI dev server that speaks the same `/nodes/ws/{device_id}` protocol as the real backend, for testing firmware without a full backend deployment.
- `partitions`: custom flash partition tables for 8MB and 16MB ESP32 variants.
- `lib/DW3000`: local DW3000 library and examples used as the source of truth for radio setup.

## Domain Value Types

Ranging commands and results are modeled as value structs in `domain/models/ranging.h`, matching the backend's own DTO-style modeling instead of loose parameter lists:

```cpp
struct RangingCommand
{
    uint16_t pan_id;
    uint16_t listener_address;
    uint16_t initiator_address;
    uint32_t timeout_uus;
};

struct RangingResult
{
    uint16_t pan_id;
    uint16_t source_address;
    uint16_t destination_address;
    float distance;
};

struct RangingFailure
{
    uint16_t pan_id;
    uint16_t source_address;
    uint16_t destination_address;
    const char *message;
};
```

`RangingCommand` maps 1:1 onto the WebSocket command payload for both `listen` and `initiate` (see below) and is threaded through `domain/contracts/ranging/stateless.h`, `domain/usecases/task/uwb_stateless.h`, `application/task/uwb_stateless/base_impl.*`, `infrastructure/ranging/stateless/dw3000_impl.*`, and `presentation/task/uwb_stateless.*` — there is no separate positional-parameter form of these calls anywhere in the codebase.

## Runtime Configuration

Runtime configuration is compiled into the firmware from a local `.env` file. `.env` is ignored by git and must exist on the machine that builds/uploads the firmware.

Expected `.env` keys:

```env
WIFI_SSID=your_wifi_ssid
WIFI_PASSWORD=your_wifi_password
UWB_SERVER_SCHEME=ws
UWB_SERVER_HOST=192.168.1.10
UWB_SERVER_PORT=8080
UWB_SERVER_PATH=/nodes/ws
```

`UWB_SERVER_SCHEME` accepts `ws`, `wss`, `ws://`, or `wss://`. The adapter normalizes it and calls:

- `WebSocketsClient::begin()` for `ws`
- `WebSocketsClient::beginSSL()` for `wss`

The server host must not include protocol, port, or path. The adapter appends the device ID to the configured path when connecting. `UWB_SERVER_PATH` must match the backend's actual mounted route, `/nodes/ws` (registered inside `presentation/http/routes/node.py` on the backend, prefix `/nodes` + `@router.websocket("/ws/{device_id}")`). For example:

```env
UWB_SERVER_SCHEME=ws
UWB_SERVER_HOST=192.168.1.50
UWB_SERVER_PORT=8080
UWB_SERVER_PATH=/nodes/ws
```

connects to:

```text
ws://192.168.1.50:8080/nodes/ws/<device_id>
```

The device ID is the ESP32 base MAC address formatted as uppercase hex without `:`.

## WebSocket Commands

The UWB task controller currently handles JSON text messages shaped like:

```json
{
  "command": 2,
  "payload": {
    "pan_id": 1234,
    "listener_address": 2222,
    "initiator_address": 1111,
    "timeout_uus": 6000
  }
}
```

This is exactly the backend's `NodeCommandCode` payload shape (`infrastructure/node/control/websocket.py` on the backend). Command codes:

- `1`: restart the device. Still requires a non-null `payload` object in the message (its contents are ignored).
- `2`: listen for a ranging poll, send the DW3000 response frame, then send an error only if the operation fails.
- `3`: initiate ranging, then send a ranging result or error.

Malformed JSON, a missing/invalid `command` or `payload`, an invalid ranging payload, or an unrecognized command code are rejected with a `warn`-level log (`presentation::task::UWBStateless`'s injected logger) — no WebSocket error frame is sent back for these cases, mirroring the backend's own `_handle_node_message` philosophy of logging rejected messages rather than always answering them.

Node messages sent back to the server use `label` and `data`:

```json
{
  "label": "ranging",
  "data": {
    "pan_id": 1234,
    "source_address": 1111,
    "destination_address": 2222,
    "distance": 2.42
  }
}
```

```json
{
  "label": "error",
  "data": {
    "pan_id": 1234,
    "source_address": 1111,
    "destination_address": 2222,
    "message": "UWB response RX timeout"
  }
}
```

Ranging timeout values use DW3000 UWB microseconds (`uus`) because that is the unit used by the DW3000 API and examples.

## Build And Upload

Use PlatformIO.

Build:

```bash
pio run -e esp32dev-8mb
pio run -e esp32dev-16mb
```

Upload:

```bash
pio run -e esp32dev-8mb -t upload
pio run -e esp32dev-16mb -t upload
```

Monitor:

```bash
pio device monitor -e esp32dev-8mb
```

If the monitor resets the board unexpectedly, add or keep these settings in `platformio.ini`:

```ini
monitor_rts = 0
monitor_dtr = 0
```

The 8MB and 16MB environments use custom partition tables. Make sure the selected environment matches the actual flash size reported by:

```bash
python -m esptool --chip esp32 --port /dev/ttyUSB0 flash_id
```

In partition CSV files, the storage subtype should stay `spiffs`; PlatformIO controls LittleFS formatting with `board_build.filesystem = littlefs`.

`lib_deps` in `platformio.ini` are pinned to PlatformIO registry names with version ranges (`bblanchon/ArduinoJson@^7.0.0`, `links2004/WebSockets@^2.4.0`) rather than unpinned git HEAD, for build reproducibility.

## Testing Against a Local Dev Server

`scripts/uwb_server_test.py` is a standalone FastAPI server that speaks the same protocol as the real backend (`/nodes/ws/{device_id}`, `command`/`payload` in, `label`/`data` out) without needing a full backend deployment. Install its dependencies and run it:

```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/uwb_server_test.py
```

It accepts connections from the three device IDs hardcoded in `DEVICE_ADDRESSES`, and once at least two are connected, cycles ranging pairs using the real backend's default scheduler timing (`listen_timeout_uus=120000`, `initiate_timeout_uus=12000`, `listen_to_initiate_delay_ms=80`, `pair_delay_ms=80`, `idle_delay_ms=250`). Incoming `"label":"ranging"`/`"error"` messages from firmware are logged distinctly.

## Development Guide

Follow the existing layer boundaries:

- Domain contracts/usecases should stay free of Arduino, DW3000, WiFi, WebSocket, and FreeRTOS details.
- Infrastructure may depend on concrete libraries and should implement exactly one domain contract.
- Application should depend on domain contracts/usecases and the logger contract, not concrete infrastructure.
- Presentation should handle runtime presentation details such as FreeRTOS loops and WebSocket callbacks.
- Composition should own concrete instances, perform hardware setup, wire dependencies, and start controllers.

Keep object ownership static where practical. The current app composition constructs concrete dependencies as members instead of allocating them dynamically.

Use the current C++ style:

- Keep implementations in matching `src/.../*.cpp` files.
- Use namespaces matching the directory structure (`contracts::`, `usecases::`, `application::`, `infrastructure::`, `presentation::`, `composition::`, `config::`).
- Use short section comments such as `// Helpers` and `// Adapter implementations`.
- Prefer small namespace-scope helper functions for file-local logic.
- Use direct early returns for invalid states.
- Keep log tags as `constexpr const char *`.
- Preserve existing snake_case member names where already used.
- Keep comments sparse and only add them where they explain non-obvious behavior.

Logging conventions:

- Infrastructure should log only what its current implementation pattern requires. The DW3000 ranging adapter currently uses error logs only.
- Application is the main place for operation logs.
- Presentation should avoid direct logs unless there is a specific reason (the UWB WebSocket command dispatcher is one such reason — it logs `warn` for malformed/unknown commands since there is no other observability point for protocol-level rejections).

When adding a new feature:

1. Add or adjust a domain model/contract/usecase first if the behavior crosses a layer boundary.
2. Implement the concrete infrastructure only against the domain contract.
3. Add application methods that coordinate contracts and logging.
4. Add or update a presentation controller if the behavior is triggered by a task, WebSocket command, HTTP request, MQTT event, or another external input.
5. Wire new concrete objects in `composition::App`.
6. Build the relevant PlatformIO environment.

## DW3000 Notes

Use `lib/DW3000/examples/range_rx/range_rx.ino` and `lib/DW3000/examples/range_tx/range_tx.ino` as references for DW3000 setup and single-sided ranging behavior.

Composition is responsible for:

- `Serial.begin`
- SPI speed and pin selection
- `spiBegin` / `spiSelect`
- `dwt_checkidlerc`
- `dwt_initialise`
- `dwt_configure`
- `dwt_configuretxrf`
- antenna delays
- LNA/PA mode

The stateless ranging infrastructure is responsible only for the ranging exchange itself:

- `initiate(command, distance)`: send poll, wait for response, compute distance. `command.initiator_address` is this device's own address, `command.listener_address` is the peer's.
- `listen(command)`: wait for poll, send response. `command.listener_address` is this device's own address, `command.initiator_address` is the peer's.

Do not move DW3000 setup into the infrastructure layer.

## Safety Notes

Do not commit `.env` or secrets. The values are still embedded into the compiled firmware binary.

Do not use destructive git or filesystem commands to recover from build issues. Prefer inspecting generated files under `.pio/`, PlatformIO output, and partition tables first.

If changing partition tables, verify the actual ESP32 flash size before upload.
