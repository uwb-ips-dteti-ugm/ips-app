# Node — `/nodes` REST (prefix, tag "Node")

Websocket scenarios (`WS /nodes/ws/{device_id}`) live in `06_node_websocket.md` — this file is REST-only. Route ordering matters here: `/nodes/registered`, `/nodes/registered/{device_id}`, `/nodes/device/{device_id}`, `/nodes/network/{network_id}/address/{address}`, and `/nodes/{device_id}/restart` are all declared before the generic `/nodes/{node_id}`, so none of them get shadowed.

**Fixtures needed**: `$ADMIN_TOKEN`, `$USER_TOKEN`, and a node network (`$NETWORK_ID`, `pan_id`) from `07_node_network.md`.

---

### NODE-01: create node success
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"device_id":"node-001","name":"Hallway sensor"}'
```
**Expected**: `200`, `NodeResponse` with `status:"pending"`, `network: null`, `address: null`.

### NODE-02: create node duplicate device_id
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"device_id":"node-001","name":"Dup"}'
```
**Expected**: `409` (unique index on `NodeDocument.device_id`).

### NODE-03: create node with `network_id` but no `address` (XOR violation)
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"device_id\":\"node-002\",\"name\":\"Bad Assign\",\"network_id\":\"$NETWORK_ID\"}"
```
**Expected**: `400` (`validate_node_network_assignment`, `"'network_id' and 'address' must be provided together."`).

### NODE-04: create node with address out of range
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"device_id\":\"node-003\",\"name\":\"X\",\"network_id\":\"$NETWORK_ID\",\"address\":70000}"
```
**Expected**: `422` (pydantic `Field(ge=0, le=0xFFFF)` on the DTO — rejected before the handler runs, not a `ValidatorDomainException`).

### NODE-05: create node with a valid network+address assignment
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"device_id\":\"node-004\",\"name\":\"Listener\",\"network_id\":\"$NETWORK_ID\",\"address\":1}"
```
**Expected**: `200`, `network.id == $NETWORK_ID`, `address:1`.

### NODE-06: create node with invalid name (single char)
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"device_id":"node-005","name":"A"}'
```
**Expected**: `400` (`validate_name`).

### NODE-07: create node missing `node/manage`
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"device_id":"node-006","name":"Nope"}'
```
**Expected**: `403`.

### NODE-08: list nodes with all filters
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/nodes?status=pending&network_id=$NETWORK_ID&address=1&is_online=false" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, filtered `PaginatedResponse`.

### NODE-09: list nodes pagination boundaries (`limit=101`→422, `page=-1`→422)
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/nodes?limit=101" -H "Authorization: Bearer $ADMIN_TOKEN"
curl -s -w '\n%{http_code}' "http://localhost:50002/nodes?page=-1" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: both `422`.

### NODE-10: get registered device ids (none connected)
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/nodes/registered -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"device_ids": []}` if no websocket clients are currently connected (run before `06_node_websocket.md`'s scenarios, or after they've all disconnected).

### NODE-11: get registration status for a specific device_id (not connected)
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/nodes/registered/node-001 -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"device_id":"node-001","is_connected":false}`.

### NODE-12: get registration status while connected
**Preconditions**: run `NODE-WS-02` from `06_node_websocket.md` first (an approved node with a live websocket connection), keep that connection open.
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/nodes/registered/node-004 -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"device_id":"node-004","is_connected":true}` — reflects the in-memory `WebSocketNodeControl.connections` dict, independent of the node's DB `status` field.

### NODE-13: get node by device_id
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/nodes/device/node-001 -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`.

### NODE-14: get node by device_id not found
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/nodes/device/does-not-exist -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### NODE-15: get node by network+address
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/nodes/network/$NETWORK_ID/address/1" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, returns `node-004`.

### NODE-16: get node by network+address not found
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/nodes/network/$NETWORK_ID/address/999" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### NODE-17: restart a not-approved node
**Preconditions**: `node-001` is still `pending` (never approved).
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes/node-001/restart -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `403` (`ForbiddenDomainException`, `"Node is not approved."`).

### NODE-18: restart an approved but not-connected node
**Preconditions**: approve `node-004` (`PATCH /nodes/{id}/status` → `"approved"`) but ensure no live websocket connection for it.
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes/node-004/restart -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `409` (`NodeNotConnectedDomainException`).

### NODE-19: restart an approved and connected node
**Preconditions**: run `NODE-WS-02` from `06_node_websocket.md` (live connection for `node-004`).
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/nodes/node-004/restart -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"message": "Node restart command sent successfully."}`. Cross-check from the websocket client side (see `NODE-WS-14` in `06_node_websocket.md`) that it actually received `{"command":1,"payload":{}}`.

### NODE-20: get node by id not found
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/nodes/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### NODE-21: update node info
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/nodes/$NODE_004_ID/info" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"description":"Renamed listener"}'
```
**Expected**: `200`.

### NODE-22: update node network assignment — reassign to a different address
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/nodes/$NODE_004_ID/network" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"network_id\":\"$NETWORK_ID\",\"address\":2}"
```
**Expected**: `200`, `address:2`.

### NODE-23: update node network assignment — unassign both to null
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/nodes/$NODE_004_ID/network" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"network_id":null,"address":null}'
```
**Expected**: `200`, `network:null`, `address:null` — both-null passes the XOR check since `None == None`.

### NODE-24: update node network assignment XOR violation
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/nodes/$NODE_004_ID/network" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"address":3}'
```
**Expected**: `400` — `network_id` omitted (defaults to `None` per the DTO) while `address` is provided.

### NODE-25: update node network assignment to an address already taken on that network
**Preconditions**: two nodes on `$NETWORK_ID`, one at address `1`.
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/nodes/$NODE_004_ID/network" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"network_id\":\"$NETWORK_ID\",\"address\":1}"
```
**Expected**: `409` — the compound unique index `(network.$id, address)` (partial, only enforced when both fields are set) rejects the conflicting reassignment.

### NODE-26: update node status — approve a pending node
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/nodes/$NODE_001_ID/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"status":"approved"}'
```
**Expected**: `200`, `status:"approved"`, `approved_at` now set.

### NODE-27: update node status invalid enum value
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/nodes/$NODE_001_ID/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"status":"unknown-status"}'
```
**Expected**: `422` (not a `NodeStatus` member).

### NODE-28: update node preferences non-object
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/nodes/$NODE_001_ID/preferences" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"preferences":[1,2,3]}'
```
**Expected**: `422`.

### NODE-29: delete node success
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/nodes/$NODE_001_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`.

### NODE-30: delete a currently-connected node
**Preconditions**: an active websocket connection for some device (e.g. `node-004` from `NODE-WS-02`).
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/nodes/$NODE_004_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200` — `application/node/node.py:delete_node` unconditionally calls `_unregister_node_connection` (best-effort, swallows any exception) before deleting the document; there is no guard blocking deletion of a connected node. `WebSocketNodeControl.unregister` (called with no explicit `connection` arg from this path, so it matches and pops unconditionally) actively closes the popped connection via `_close_connection`, which closes with code `1000` (normal closure). So the live websocket client should observe a `1000` close as a direct side effect of this delete call, not just silently forgotten server-side. Confirm the client actually receives that close frame.

### NODE-31: delete nonexistent node
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/nodes/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.
