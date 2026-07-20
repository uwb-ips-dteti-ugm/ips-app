# NodeNetwork — `/node-networks` (prefix, tag "NodeNetwork")

Endpoints: `POST /node-networks`, `GET /node-networks`, `GET /node-networks/pan/{pan_id}`, `GET /node-networks/{id}`, `PATCH /node-networks/{id}`, `DELETE /node-networks/{id}`. Route ordering: `/pan/{pan_id}` is declared before the generic `/{id}`, so it isn't shadowed.

**Fixtures needed**: `$ADMIN_TOKEN`, `$USER_TOKEN`. This file's `NETNET-01` fixture (`$NETWORK_ID`, `pan_id:1`) is the one referenced as `$NETWORK_ID` throughout `05_node.md` and `08_ranging.md` — run this file first if following the suggested cross-file order.

---

### NETNET-01: create node network success
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/node-networks \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"pan_id":1,"name":"lab-network","description":"Lab UWB network"}'
```
**Expected**: `200`, `NodeNetworkResponse` echoing fields.

### NETNET-02: create node network duplicate pan_id
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/node-networks \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"pan_id":1,"name":"dup-network"}'
```
**Expected**: `409` (unique index on `NodeNetworkDocument.pan_id`).

### NETNET-03: create node network pan_id out of range
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/node-networks \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"pan_id":70000,"name":"bad-pan"}'
```
**Expected**: `422` (pydantic `Field(ge=0, le=0xFFFF)`).

### NETNET-04: create node network invalid name
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/node-networks \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"pan_id":2,"name":"A"}'
```
**Expected**: `400` (`validate_name`, min 2 chars).

### NETNET-05: create node network missing `node-network/manage`
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/node-networks \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"pan_id":3,"name":"whatever"}'
```
**Expected**: `403`.

### NETNET-06: list node networks
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/node-networks -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, includes `lab-network`.

### NETNET-07: get node network by pan_id
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/node-networks/pan/1 -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`.

### NETNET-08: get node network by pan_id not found
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/node-networks/pan/9999 -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### NETNET-09: get node network by id not found
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/node-networks/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### NETNET-10: update node network name/description
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/node-networks/$NETWORK_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"description":"Updated lab network"}'
```
**Expected**: `200`.

### NETNET-11: update node network to an already-taken pan_id
**Preconditions**: a second network exists at `pan_id:2` (create one first: `{"pan_id":2,"name":"second-network"}`).
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/node-networks/$SECOND_NETWORK_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"pan_id":1}'
```
**Expected (as originally documented)**: `409`.

**ACTUALLY OBSERVED (run against a live deployment)**: `500`, body `{"error": ""}` (empty message). **This is a confirmed code bug, root-caused precisely, not a flaky test**: `infrastructure/repository/node_network/beanie.py:update_node_network_by_id` wraps `await doc.set(update_data, session=session)` in `except DuplicateKeyError as e: raise DuplicateDomainException(...)`, expecting Beanie to surface a `pymongo.errors.DuplicateKeyError` the same way `.insert()` does on `create_node_network`. It doesn't. Reproduced directly against the running container:
```python
# docker exec ips-app-backend python3 -c "... await doc.set({'pan_id': <taken>}) ..."
# EXCEPTION TYPE: <class 'beanie.exceptions.RevisionIdWasChanged'>  STR: ''
```
Beanie's `Document.set()` uses its optimistic-concurrency revision mechanism: when the underlying `update_one` reports zero matched documents (which is what actually happens here, because the write is rejected by the unique index before Beange's revision check even matters), Beanie interprets that as "the document's revision changed underneath us" and raises `RevisionIdWasChanged()` — a different exception with an **empty** `str()` — instead of ever letting `DuplicateKeyError` bubble up. The repo's `except DuplicateKeyError` clause is therefore dead code for this failure path; the exception falls through to the generic `except Exception as e: raise UnexpectedDomainException(str(e))`, producing the empty-body `500`.

**This is a systemic bug, not isolated to node-networks** — `infrastructure/repository/permission/beanie.py:update_permission_by_id` and `infrastructure/repository/role/beanie.py:update_role_by_id` use the identical `.set()` + `except DuplicateKeyError` pattern for their own unique `name` fields, and both were confirmed to fail identically:
```
permission rename-to-dup: 500 {"error":""}
role rename-to-dup: 500 {"error":""}
```
See `PERM-15` in `04_permission.md` and `ROLE-23` in `03_role.md` for the same bug confirmed on those entities. **Node's own `update_node_network_assignment_by_id` is NOT affected** — it uses a proactive `find_one`-then-raise `_ensure_network_address_is_available` check before ever calling `.set()`, rather than relying on catching a write-time exception, so `NODE-25` (address-reassignment conflict) is unaffected and correctly returns `409`; this is the actual pattern to converge the other three repositories on when this gets fixed.

**FIXED**: `update_node_network_by_id` now catches `(DuplicateKeyError, RevisionIdWasChanged)` together, converting either to `DuplicateDomainException`. Re-verified live: updating a node-network's `pan_id` to an already-taken value now returns `409 {"error": "PAN ID ... already exists"}` instead of `500`. The same fix was applied to `PERM-15`/`ROLE-23`'s repos (`permission`/`role`).

### NETNET-12: delete node network success
**Preconditions**: `$SECOND_NETWORK_ID` has no nodes assigned.
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/node-networks/$SECOND_NETWORK_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"message": "Node network deleted successfully."}`.

### NETNET-13: delete node network still referenced by a node
**Preconditions**: `$NETWORK_ID` has at least one node assigned to it (e.g. `node-004` from `NODE-05`/`NODE-22` in `05_node.md`).
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/node-networks/$NETWORK_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `403` — `infrastructure/repository/node_network/beanie.py:delete_node_network_by_id` explicitly checks for a referencing `NodeDocument` and raises `ForbiddenDomainException("Node network is used by a node.")` if found (confirmed by reading the repository source directly). Not a cascading delete.

### NETNET-14: delete node network missing `node-network/delete`, and delete nonexistent
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/node-networks/$NETWORK_ID" -H "Authorization: Bearer $USER_TOKEN"
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/node-networks/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: first call `403`; second call `404`.
