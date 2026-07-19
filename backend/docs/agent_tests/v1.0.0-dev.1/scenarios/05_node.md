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
**Preconditions**: **the node must already have a `network`+`address` assigned** — confirmed by running against a plain unassigned node first: approving it returns `400 {"error":"A node must have a network and address before approval."}` (a real, correctly-enforced business rule, not a bug — this scenario's original write-up omitted this precondition). Assign one first if not already set: `PATCH /nodes/$NODE_001_ID/network` with `{"network_id":"$NETWORK_ID","address":4}`.
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

### NODE-32: `PATCH /nodes/{id}/network` silently corrupts the node's `network` field from a Link into an embedded copy — CRITICAL bug, discovered during execution, not in the original plan

**This is the single most severe finding in this entire test pass.** It was found while investigating why `NODE-WS-10` (in `06_node_websocket.md`) couldn't find a node it should have found, and turned out to be a real, reproducible data-integrity bug with consequences well beyond that one symptom.

**Root cause**: `infrastructure/repository/node/beanie.py:update_node_network_assignment_by_id` builds its partial update as:
```python
network = await self._read_node_network_document(network_id, session)   # a full NodeNetworkDocument instance
...
await doc.set({"network": network, "address": address, ...}, session=session)
```
Compare this to `create_node`, which does `network=cast(Optional[Link[NodeNetworkDocument]], network)` before `doc.insert(...)` — `Document.insert()` respects the field's declared Pydantic type (`Node.network: Optional[Link[NodeNetworkDocument]]`) and serializes it as a proper Mongo `DBRef` (`{"$ref": "node_networks", "$id": ObjectId(...)}`). **`Document.set()` does not** — it performs a raw partial `$set` that bypasses the model's Link-aware serialization, so handing it a raw `NodeNetworkDocument` instance embeds the ENTIRE document as a nested subdocument (with `_id`, not `$id`) instead of storing a reference.

**Reproduced directly against the raw MongoDB documents**:
```bash
# a node whose network was set at CREATION time (POST /nodes) — correct:
db.nodes.findOne({device_id:"freshnode-created"}, {network:1})
# network: DBRef('node_networks', ObjectId('...'))

# a node whose network was set via PATCH /nodes/{id}/network — corrupted:
db.nodes.findOne({device_id:"corrupt-test-b"}, {network:1})
# network: { _id: ObjectId('...'), revision_id: null, pan_id: 1, name: 'lab-network', ... }  <- fully embedded, not a DBRef
```

**Consequences, both confirmed live**:
1. **Node-by-network+address lookups silently stop finding the node.** `GET /nodes/network/{network_id}/address/{address}` and `ranging` reports both query via `NODE_NETWORK_ID_FIELD = "network.$id"` (`infrastructure/repository/node/beanie.py`). A corrupted node has no `network.$id` path anymore (it has `network._id` instead), so the query never matches it. This is exactly why `NODE-WS-10` failed to record a ranging measurement for `node-004` even though it was a real, approved, correctly-assigned node — its network field had been silently corrupted by the `NODE-22`/`NODE-23`/`NODE-25` reassignment calls run earlier in this same test pass.
2. **The network+address uniqueness guarantee silently stops applying to a corrupted node — in both directions, proven with a live reproduction**:
   - `_ensure_network_address_is_available` (the app-level pre-check `update_node_network_assignment_by_id` uses before writing) queries by `network.$id`, so it cannot see a corrupted node occupying an address, and will happily let a *different* node move onto that same address.
   - The DB-level compound unique index on `(network.$id, address)` has a **partial filter** `{"network.$id": {"$exists": true}, "address": {"$exists": true}}` (see `infrastructure/repository/node/beanie_model.py`) — once a node's field is `network._id` instead of `network.$id`, it falls **outside the partial filter's scope entirely**, so the unique index doesn't apply to it either.
   - **Live proof**: created node A with `network_id`+`address:60` at creation time (proper Link). Created node B plain, then `PATCH`-assigned it to `address:61` (this corrupts B's `network` field). Then `PATCH`-assigned A to `address:61` too (B's already-occupied address) — **this succeeded with `200`**, when it should have been rejected `409`. A follow-up raw Mongo query confirmed **both A and B ended up simultaneously at `address:61` on the same network**, with no error raised anywhere in the stack.

**Blast radius**: any node whose network assignment is ever changed after creation via `PATCH /nodes/{id}/network` — which is the realistic, expected operational path for reassigning nodes over time, not an edge case — permanently loses both (a) discoverability by network+address lookup, including for ranging reports, and (b) the address-uniqueness guarantee for its network, from that point forward. Nodes that only ever get their network set once at creation time and never touched again are unaffected.

**Suggested fix direction**: `update_node_network_assignment_by_id` should build the update payload the same way `create_node` effectively relies on Beanie to do at the type level — either explicitly construct the DBRef-shaped value before calling `.set()` (e.g. `Link(ref=DBRef(...), document_class=NodeNetworkDocument)` or equivalent), or avoid `.set()` for this field entirely and instead re-save the whole document via a path that goes through the model's normal Link serialization.

**Test hygiene note**: this means every scenario in this file that exercises `PATCH /nodes/{id}/network` (`NODE-22` through `NODE-25`) leaves the affected node in this corrupted state afterward — `node-004` in particular is corrupted for the remainder of this test pass once `NODE-22` runs, which is exactly why it had to be worked around when writing `08_ranging.md`'s fixtures (see that file's notes).

**FIXED**: `update_node_network_assignment_by_id` (`infrastructure/repository/node/beanie.py`) now explicitly wraps the fetched network as `Link(DBRef(NodeNetworkDocument.Settings.name, network.id), NodeNetworkDocument)` before handing it to `.set()`, instead of the raw fetched `NodeNetworkDocument`. Re-verified live end-to-end: (1) a node's `network` field stored via `PATCH` is now a proper `DBRef` in the raw Mongo document, matching what `POST /nodes` produces at creation; (2) `GET /nodes/network/{id}/address/{addr}` correctly finds a node after its network was reassigned via `PATCH`; (3) attempting to reassign a second node onto an address already held by a `PATCH`-reassigned node now correctly returns `409` instead of silently succeeding — the exact live reproduction from this writeup, re-run, now behaves correctly.
