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
**Expected**: `409`.

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
