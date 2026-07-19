# Ranging — `/ranging` (prefix, tag "Ranging")

None of these routes use `Depends(get_claims)` for attribution — ranging reports/reads aren't tied to the calling user, only gated by permission. Note `POST /ranging/report` (this file, requires JWT + `ranging/manage`) is a distinct path from the no-auth-at-all websocket ranging message (`NODE-WS-10`/`NODE-WS-11` in `06_node_websocket.md`) — both ultimately call the same `RangingUsecase.report_ranging_measurement`, just from different entry points with different auth requirements.

**Fixtures needed**: `$ADMIN_TOKEN`, `$USER_TOKEN`, a node network `$NETWORK_ID` (pan_id `1`, from `07_node_network.md`), and two **approved** nodes on that network at distinct addresses: `node-004` (address `1`, `$NODE_004_ID`, `$NODE_004_DEVICE_ID="node-004"`) and a second node, e.g. `node-005` (address `2`, approved) — create/approve it via `05_node.md`'s patterns if not already present.

`report_ranging_measurement` maps `source_address` → `listener_node`, `destination_address` → `initiator_node` in the resulting `RangingRecord`, and requires `reported_by_device_id == source_node.device_id` (the reporting device must be the "source"/listener side of the measurement) — confirmed by reading `application/ranging/ranging.py` directly.

---

### RANGE-01: report ranging measurement success
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging/report \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"reported_by_device_id":"node-004","pan_id":1,"source_address":1,"destination_address":2,"distance":1.5}'
```
**Expected**: `200`, `RangingRecordResponse` with `listener_node.device_id:"node-004"`, `initiator_node.device_id:"node-005"`, `distance:1.5`.

### RANGE-02: report with `reported_by_device_id` not matching the source node
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging/report \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"reported_by_device_id":"node-005","pan_id":1,"source_address":1,"destination_address":2,"distance":1.5}'
```
**Expected**: `403` (`"Node ranging source must match the reporting device ID."`) — `node-005` claims to report a measurement where address `1` (`node-004`) is the source.

### RANGE-03: report referencing an unapproved node
**Preconditions**: temporarily set `node-005`'s status back to `pending` (`PATCH /nodes/{id}/status`).
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging/report \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"reported_by_device_id":"node-004","pan_id":1,"source_address":1,"destination_address":2,"distance":1.5}'
```
**Expected**: `403` (`_ensure_approved`, node-005 is `destination_node` and not approved). Restore `node-005` to `approved` afterward.

### RANGE-04: report with unknown pan_id
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging/report \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"reported_by_device_id":"node-004","pan_id":9999,"source_address":1,"destination_address":2,"distance":1.5}'
```
**Expected**: `404` (network lookup by `pan_id` fails first, before either node lookup).

### RANGE-05: report with unknown address on a valid network
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging/report \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"reported_by_device_id":"node-004","pan_id":1,"source_address":1,"destination_address":250,"distance":1.5}'
```
**Expected**: `404` (destination node lookup by `(network_id, address=250)` fails).

### RANGE-06: report with negative distance
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging/report \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"reported_by_device_id":"node-004","pan_id":1,"source_address":1,"destination_address":2,"distance":-1}'
```
**Expected**: `422` (pydantic `Field(ge=0)` on `ReportRangingMeasurementRequest.distance` — rejected before the handler runs).

### RANGE-07: report with address out of uwb range
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging/report \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"reported_by_device_id":"node-004","pan_id":1,"source_address":70000,"destination_address":2,"distance":1.5}'
```
**Expected**: `422` (pydantic `Field(ge=0, le=0xFFFF)`).

### RANGE-08: report missing `ranging/manage`
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging/report \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"reported_by_device_id":"node-004","pan_id":1,"source_address":1,"destination_address":2,"distance":1.5}'
```
**Expected**: `403`.

### RANGE-09: list ranging records by interval
**Preconditions**: `RANGE-01` produced at least one record.
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/ranging?start=2020-01-01T00:00:00Z&end=2099-01-01T00:00:00Z" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `List[RangingRecordResponse]` including the `RANGE-01` record.

### RANGE-10: list ranging records `start == end` (allowed boundary)
```bash
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
curl -s -w '\n%{http_code}' "http://localhost:50002/ranging?start=$NOW&end=$NOW" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200` (not an error — `validate_record_interval` only rejects `start > end`, `start == end` is explicitly allowed). Likely an empty list unless a record was recorded at exactly that instant.

### RANGE-11: list ranging records `start > end`
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/ranging?start=2099-01-01T00:00:00Z&end=2020-01-01T00:00:00Z" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `400` (`"The interval start must be before or equal to the interval end."`).

### RANGE-12: list ranging records missing required `start`/`end`
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/ranging -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `422` — `start`/`end` are `Query(...)` (required), FastAPI rejects the request before the handler runs.

### RANGE-13: list ranging records filtered by network_id/node_id
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/ranging?start=2020-01-01T00:00:00Z&end=2099-01-01T00:00:00Z&network_id=$NETWORK_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, filtered to that network.

### RANGE-14: get latest ranging record
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/ranging/latest -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, the most recent `RangingRecordResponse` (matches `RANGE-01`'s record if no later ones exist).

### RANGE-15: get latest ranging record when none match
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/ranging/latest?network_id=000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, body `null` (not `404` — the endpoint's response type is `Optional[RangingRecordResponse]`).

### RANGE-16: delete ranging records by interval
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/ranging?start=2020-01-01T00:00:00Z&end=2099-01-01T00:00:00Z" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"deleted_count": <n>}` reflecting however many records existed in that interval. Missing `ranging/delete` → `403` (test with `$USER_TOKEN`).
