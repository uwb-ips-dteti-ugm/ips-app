# Node Websocket — `WS /nodes/ws/{device_id}`

This route has **no `permission_check`/`authorization_check` dependency at all** — any client can attempt to open it with an arbitrary `device_id`. Authentication for node control-plane actions happens implicitly through node approval status, not JWT.

curl can't drive a websocket conversation, so every scenario here uses a short Python snippet (`websockets` — already pinned in `requirements.txt`, available in the project's `.venv`). Run these with `python3 -m asyncio` interactively or save as a throwaway script; each snippet is intentionally short and self-contained.

**Fixtures needed**: none beyond a reachable server at `ws://localhost:50002`. Node documents get auto-created by connecting (see `NODE-WS-01`), so this file doesn't strictly depend on `05_node.md`'s fixtures, though several scenarios below cross-reference `05_node.md`'s REST scenarios for verification (e.g. `NODE-WS-02` needs the node approved via `PATCH /nodes/{id}/status`, which is a `05_node.md` REST call).

---

### NODE-WS-01: connect with a brand-new device_id → auto-registers pending → rejected
```python
import asyncio, websockets

async def main():
    try:
        async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
            await ws.recv()
    except websockets.exceptions.ConnectionClosedError as e:
        print("close code:", e.code, "reason:", e.reason)

asyncio.run(main())
```
**Expected**: connection is rejected before `accept()` — close code `1008`, reason `"Node is not approved."`. Confirm via REST that a `Node` document was nonetheless auto-created: `curl http://localhost:50002/nodes/device/ws-test-01 -H "Authorization: Bearer $ADMIN_TOKEN"` → `200`, `status:"pending"`, `name` is a randomly-generated display name (not `"ws-test-01"`), `description:"Registered from node websocket connection"`.

### NODE-WS-02: approve, then reconnect → accepted
**Preconditions**: `NODE-WS-01` ran (node exists), then as admin: `PATCH /nodes/{id}/status` `{"status":"approved"}`.
```python
import asyncio, websockets

async def main():
    async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
        print("connected, staying open for 5s")
        await asyncio.sleep(5)

asyncio.run(main())
```
**Expected**: connection is accepted (no exception, `ws.recv()` blocks rather than raising). Confirm `last_connected_at` is now set via `GET /nodes/device/ws-test-01`, and `GET /nodes/registered/ws-test-01` → `is_connected:true` while this script is still running.

### NODE-WS-03: second connection for the same device_id evicts the first
**Preconditions**: `NODE-WS-02`'s connection still open in one process/terminal.
```python
import asyncio, websockets

async def main():
    async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws2:
        print("second connection open")
        await asyncio.sleep(3)

asyncio.run(main())
```
**Expected**: the *first* connection (from `NODE-WS-02`) receives a close frame with code `1000` (normal closure) almost immediately after this second connection is established — observe this on the first script's side (it should raise `ConnectionClosedOK` with `code=1000` on its next `recv()`/naturally when the `async with` block exits). The second connection stays open and is now the one `GET /nodes/registered/ws-test-01` reports as connected.

### NODE-WS-04: graceful client-initiated disconnect
**Preconditions**: any accepted connection (e.g. re-run `NODE-WS-02`'s snippet but let the `async with` block exit naturally instead of sleeping).
```python
import asyncio, websockets

async def main():
    async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
        pass  # connect then immediately close cleanly

asyncio.run(main())
```
**Expected**: no server-side error. Confirm via `GET /nodes/device/ws-test-01` that `last_disconnected_at` is now set, and `GET /nodes/registered/ws-test-01` → `is_connected:false`.

### NODE-WS-05: heartbeat event → connection stays open, no-op
```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
        await ws.send(json.dumps({"event": "heartbeat"}))
        await asyncio.sleep(1)
        print("still open, no close received")

asyncio.run(main())
```
**Expected**: no exception, no close frame — `event:"heartbeat"` is a recognized no-op (`_handle_node_message`).

### NODE-WS-06: ack event → connection stays open, no-op
```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
        await ws.send(json.dumps({"event": "ack"}))
        await asyncio.sleep(1)
        print("still open, no close received")

asyncio.run(main())
```
**Expected**: no exception, no close frame — `event:"ack"` is a recognized no-op.

### NODE-WS-07: unrecognized message shape (neither `label` nor `event`) → connection closed
```python
import asyncio, json, websockets

async def main():
    try:
        async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
            await ws.send(json.dumps({"foo": "bar"}))
            await ws.recv()
    except websockets.exceptions.ConnectionClosedError as e:
        print("close code:", e.code, "reason:", e.reason)

asyncio.run(main())
```
**Expected**: close code `1008`, reason `"Unsupported node websocket message."` — a single malformed message terminates the WHOLE connection, it does not just get ignored.

### NODE-WS-08: invalid JSON text → connection closed
```python
import asyncio, websockets

async def main():
    try:
        async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
            await ws.send("not valid json{{{")
            await ws.recv()
    except websockets.exceptions.ConnectionClosedError as e:
        print("close code:", e.code, "reason:", e.reason)

asyncio.run(main())
```
**Expected**: close code `1008`, reason `"Node websocket message must be valid JSON."`.

### NODE-WS-09: JSON array instead of a JSON object → connection closed
```python
import asyncio, json, websockets

async def main():
    try:
        async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
            await ws.send(json.dumps([1, 2, 3]))
            await ws.recv()
    except websockets.exceptions.ConnectionClosedError as e:
        print("close code:", e.code, "reason:", e.reason)

asyncio.run(main())
```
**Expected**: close code `1008`, reason `"Node websocket message must be a JSON object."`.

### NODE-WS-10: valid `label:"ranging"` message → connection stays open even if the measurement itself is rejected
**Preconditions**: some `pan_id`/addresses that likely don't correspond to real approved+assigned nodes (to specifically exercise the "domain rejection doesn't close the socket" path) — or use real ones from `07_node_network.md`/`05_node.md` fixtures to exercise the accepted path instead.
```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
        await ws.send(json.dumps({
            "label": "ranging",
            "data": {"pan_id": 1, "source_address": 1, "destination_address": 2, "distance": 1.23},
        }))
        await asyncio.sleep(1)
        print("still open")

asyncio.run(main())
```
**Expected**: connection stays open regardless of whether the measurement is accepted or rejected as a `DomainException` (e.g. unknown network/node, node not approved, `ws-test-01` not matching the reporting device) — rejections are only logged server-side (`"Rejected ranging measurement from node websocket"`), never surfaced to the client or closed. If the measurement WAS accepted (real fixtures used), confirm via `GET /ranging/latest` as admin.

### NODE-WS-11: `label:"ranging"` missing a required `data` key → connection closed with `1011`
```python
import asyncio, json, websockets

async def main():
    try:
        async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
            await ws.send(json.dumps({"label": "ranging", "data": {"pan_id": 1}}))  # missing source/destination/distance
            await ws.recv()
    except websockets.exceptions.ConnectionClosedError as e:
        print("close code:", e.code, "reason:", e.reason)

asyncio.run(main())
```
**Expected**: close code `1011` (internal error), NOT `1008` — `_handle_ranging_message` accesses `data["source_address"]` etc. via plain dict indexing with no `.get()`/try-except around it, so a missing key raises a bare `KeyError`, which is not a `DomainException` and isn't caught by the specific ranging-rejection handler; it propagates as an unhandled exception to the outer generic `except Exception` in `connect_node_websocket`, producing `1011` with reason `"Something went wrong while connecting the node."`. **This is a real inconsistency** worth flagging as a discovered quirk: a malformed ranging payload behaves differently (hard close, 1011) from a semantically-rejected-but-well-formed one (silent log, stays open, per `NODE-WS-10`).

### NODE-WS-12: `label:"error"` → no-op
```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01") as ws:
        await ws.send(json.dumps({"label": "error", "message": "node reported an internal fault"}))
        await asyncio.sleep(1)
        print("still open")

asyncio.run(main())
```
**Expected**: connection stays open; server only logs at debug level, no other effect.

### NODE-WS-13: `WebSocketDisconnect` mid-loop is handled silently
```python
import asyncio, websockets

async def main():
    ws = await websockets.connect("ws://localhost:50002/nodes/ws/ws-test-01")
    await ws.close(code=1000)

asyncio.run(main())
```
**Expected**: no server-side error logged (check `docker compose logs backend` around this timestamp) — a clean client close is handled by the `except WebSocketDisconnect: pass` branch, not the generic exception path.

### NODE-WS-14: server→node `RESTART` command payload (cross-reference `NODE-19` in `05_node.md`)
**Preconditions**: an approved, connected node (keep a script like `NODE-WS-02`'s open on `node-004` or another approved device_id).
```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:50002/nodes/ws/node-004") as ws:
        print("waiting for a command...")
        msg = await ws.recv()
        print("received:", msg)

asyncio.run(main())
```
While this is running, from another shell trigger `curl -X POST http://localhost:50002/nodes/node-004/restart -H "Authorization: Bearer $ADMIN_TOKEN"` (`NODE-19`).
**Expected**: the websocket client's `recv()` returns exactly `{"command": 1, "payload": {}}` (`NodeCommandCode.RESTART = 1`), and the REST call returns `200`.
