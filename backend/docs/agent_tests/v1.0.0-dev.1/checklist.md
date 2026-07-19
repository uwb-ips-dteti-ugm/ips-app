# API Test Checklist — v1.0.0-dev.1

193 scenarios (189 originally planned + 4 discovered during execution/regression) across 8 entities, the node websocket protocol, and cross-cutting concerns. 7 real bugs were found and have since been fixed — see the **BUG FOUND, FIXED** entries below. Full request/response detail, curl/Python snippets, and preconditions for every item live in `scenarios/*.md` — this file is the skimmable master list. See `scenarios/00_environment_and_setup.md` before running anything (deployment, seeded accounts, token-expiry caveat).

Check a box only once the scenario has actually been run against a deployed instance and the observed result matches (or once a discovered discrepancy has been noted inline).

## Auth — `scenarios/01_auth.md`

- [x] AUTH-01 — sign-in success
- [x] AUTH-02 — sign-in wrong password
- [x] AUTH-03 — sign-in unknown username — **BUG FOUND, FIXED**: was returning `404` (username-enumeration leak); now returns `401` like wrong-password — see scenario doc
- [x] AUTH-04 — sign-in empty username/password
- [x] AUTH-05 — sign-in as a suspended user
- [x] AUTH-06 — sign-in as a banned user
- [x] AUTH-07 — refresh-token success
- [x] AUTH-08 — refresh-token expired (documents why this is impractical to test directly; see XCUT-03 for the equivalent access-token expiry test)
- [x] AUTH-09 — refresh-token with an access token instead — **CONFIG WEAKNESS FOUND, FIXED**: `.env`/`.env.example` now use distinct token secrets; correctly returns `401` — see scenario doc
- [x] AUTH-10 — refresh-token malformed string
- [x] AUTH-11 — register success
- [x] AUTH-12 — register without `auth/manage` permission
- [x] AUTH-13 — register duplicate username
- [x] AUTH-14 — register with invalid `role_id`
- [x] AUTH-15 — register with weak password (< 8 chars)
- [x] AUTH-16 — register with invalid username (starts with non-alnum)
- [x] AUTH-17 — change-own-password success
- [x] AUTH-18 — change-own-password wrong old password
- [x] AUTH-19 — change-own-password weak new password
- [x] AUTH-20 — change-own-password no auth
- [x] AUTH-21 — admin reset-password success
- [x] AUTH-22 — admin reset-password missing `auth/manage`
- [x] AUTH-23 — admin reset-password nonexistent user_id

## User — `scenarios/02_user.md`

- [x] USER-01 — get own profile
- [x] USER-02 — get own profile no auth
- [x] USER-03 — get own permissions
- [x] USER-04 — get own permissions as `user` (zero permissions)
- [x] USER-05 — update own info success
- [x] USER-06 — update own info invalid name (below 2-char minimum)
- [x] USER-07 — update own info invalid username (consecutive dots)
- [x] USER-08 — update own bio too long (> 2000 chars)
- [x] USER-09 — update own preferences success
- [x] USER-10 — update own preferences non-object value
- [x] USER-11 — list users default pagination
- [x] USER-12 — list users `limit=101` (over max)
- [x] USER-13 — list users `limit=0`
- [x] USER-14 — list users `page=-1`
- [x] USER-15 — list users search no match
- [x] USER-16 — list users filtered by `role_id`/`status`
- [x] USER-17 — list users missing `user/view`
- [x] USER-18 — get user by id
- [x] USER-19 — get user by id not found
- [x] USER-20 — get user permissions by id
- [x] USER-21 — admin update user role
- [x] USER-22 — admin update user role with invalid role_id
- [x] USER-23 — admin update user status (valid enum)
- [x] USER-24 — admin update user status invalid enum value
- [x] USER-25 — admin update info/preferences/role/status without `user/manage`
- [x] USER-26 — delete user success
- [x] USER-27 — delete user missing `user/delete`
- [x] USER-28 — delete nonexistent user
- [x] USER-29 — admin deletes their own currently-authenticated account

## Role — `scenarios/03_role.md`

- [x] ROLE-01 — create role success
- [x] ROLE-02 — create role duplicate name
- [x] ROLE-03 — create role invalid resource-name (starts with non-alnum)
- [x] ROLE-04 — create role missing `role/manage`
- [x] ROLE-05 — list roles
- [x] ROLE-06 — get default role
- [x] ROLE-07 — get role by id
- [x] ROLE-08 — get role by id not found
- [x] ROLE-09 — get role permissions
- [x] ROLE-10 — update role name/description
- [x] ROLE-11 — `PATCH /roles/{id}/default` unsets the previous default
- [x] ROLE-12 — update role preferences non-object
- [x] ROLE-13 — add permissions to role (incl. idempotent re-add)
- [x] ROLE-14 — add permissions empty list
- [x] ROLE-15 — add permissions with a nonexistent id in the list
- [x] ROLE-16 — remove permissions from role
- [x] ROLE-17 — add/remove permissions missing `role/manage`
- [x] ROLE-18 — delete role success
- [x] ROLE-19 — delete role currently assigned to a user
- [x] ROLE-20 — delete role missing `role/delete`
- [x] ROLE-21 — delete nonexistent role
- [x] ROLE-22 — delete the seeded default role (documents the two possible branches; not to be run destructively on a kept environment)
- [x] ROLE-23 — rename a role to an already-taken name — **BUG FOUND, FIXED**: now catches `RevisionIdWasChanged` alongside `DuplicateKeyError`, returns `409` — see NETNET-11

## Permission — `scenarios/04_permission.md`

- [x] PERM-01 — create permission success
- [x] PERM-02 — create permission duplicate name
- [x] PERM-03 — create permission invalid resource-name
- [x] PERM-04 — create permission missing `permission/manage`
- [x] PERM-05 — list permissions
- [x] PERM-06 — list permissions search
- [x] PERM-07 — list permissions missing `permission/view`
- [x] PERM-08 — get permission by id
- [x] PERM-09 — get permission by id not found
- [x] PERM-10 — update permission name/description
- [x] PERM-11 — update permission preferences non-object
- [x] PERM-12 — delete permission success
- [x] PERM-13 — delete permission currently attached to a role
- [x] PERM-14 — delete permission missing `permission/delete`, and delete nonexistent
- [x] PERM-15 — rename a permission to an already-taken name — **BUG FOUND, FIXED**: now catches `RevisionIdWasChanged` alongside `DuplicateKeyError`, returns `409` — see NETNET-11

## Node — `scenarios/05_node.md`

- [x] NODE-01 — create node success
- [x] NODE-02 — create node duplicate device_id
- [x] NODE-03 — create node with `network_id` but no `address` (XOR violation)
- [x] NODE-04 — create node with address out of range
- [x] NODE-05 — create node with a valid network+address assignment
- [x] NODE-06 — create node with invalid name
- [x] NODE-07 — create node missing `node/manage`
- [x] NODE-08 — list nodes with all filters
- [x] NODE-09 — list nodes pagination boundaries
- [x] NODE-10 — get registered device ids (none connected)
- [x] NODE-11 — get registration status for a device_id (not connected)
- [x] NODE-12 — get registration status while connected
- [x] NODE-13 — get node by device_id
- [x] NODE-14 — get node by device_id not found
- [x] NODE-15 — get node by network+address
- [x] NODE-16 — get node by network+address not found
- [x] NODE-17 — restart a not-approved node
- [x] NODE-18 — restart an approved but not-connected node
- [x] NODE-19 — restart an approved and connected node
- [x] NODE-20 — get node by id not found
- [x] NODE-21 — update node info
- [x] NODE-22 — update node network assignment — reassign to a different address (see **NODE-32**: this call is the trigger for a critical data-corruption bug)
- [x] NODE-23 — update node network assignment — unassign both to null
- [x] NODE-24 — update node network assignment XOR violation
- [x] NODE-25 — update node network assignment to an address already taken
- [x] NODE-26 — update node status — approve a pending node (discovered precondition: node must already have a network+address assigned, or this correctly returns 400 first — see scenario doc)
- [x] NODE-27 — update node status invalid enum value
- [x] NODE-28 — update node preferences non-object
- [x] NODE-29 — delete node success
- [x] NODE-30 — delete a currently-connected node
- [x] NODE-31 — delete nonexistent node
- [x] NODE-32 — `PATCH /nodes/{id}/network` silently corrupts the node's Link field into an embedded copy — **CRITICAL BUG FOUND, FIXED**: now wraps the network as a proper `Link`/`DBRef` before `.set()`; lookups and address-uniqueness both confirmed working again live. See scenario doc.

## Node Websocket — `scenarios/06_node_websocket.md`

- [x] NODE-WS-01 — connect with a brand-new device_id → auto-registers pending → rejected (observed as HTTP 403 at the handshake itself, since rejection happens before `accept()` — not a post-upgrade 1008 close frame; documented as a transport-level nuance, not a bug)
- [x] NODE-WS-02 — approve, then reconnect → accepted
- [x] NODE-WS-03 — second connection for the same device_id evicts the first (old closed 1000)
- [x] NODE-WS-04 — graceful client-initiated disconnect
- [x] NODE-WS-05 — heartbeat event → connection stays open, no-op
- [x] NODE-WS-06 — ack event → connection stays open, no-op
- [x] NODE-WS-07 — unrecognized message shape → connection closed (1008)
- [x] NODE-WS-08 — invalid JSON text → connection closed (1008)
- [x] NODE-WS-09 — JSON array instead of object → connection closed (1008)
- [x] NODE-WS-10 — valid ranging message → connection stays open even if the measurement is rejected (confirmed; but also surfaced **NODE-32**, the critical node-network-corruption bug, via an unexpected rejection — see scenario doc)
- [x] NODE-WS-11 — ranging message missing a required data key → connection closed (1011, discovered inconsistency vs. NODE-WS-10)
- [x] NODE-WS-12 — `label:"error"` → no-op
- [x] NODE-WS-13 — `WebSocketDisconnect` mid-loop handled silently
- [x] NODE-WS-14 — server→node RESTART command payload verification (cross-ref NODE-19)

## NodeNetwork — `scenarios/07_node_network.md`

- [x] NETNET-01 — create node network success
- [x] NETNET-02 — create node network duplicate pan_id
- [x] NETNET-03 — create node network pan_id out of range
- [x] NETNET-04 — create node network invalid name
- [x] NETNET-05 — create node network missing `node-network/manage`
- [x] NETNET-06 — list node networks
- [x] NETNET-07 — get node network by pan_id
- [x] NETNET-08 — get node network by pan_id not found
- [x] NETNET-09 — get node network by id not found
- [x] NETNET-10 — update node network name/description
- [x] NETNET-11 — update node network to an already-taken pan_id — **BUG FOUND, FIXED**: now catches `RevisionIdWasChanged` alongside `DuplicateKeyError`, returns `409` — same fix applied to PERM-15, ROLE-23
- [x] NETNET-12 — delete node network success
- [x] NETNET-13 — delete node network still referenced by a node
- [x] NETNET-14 — delete node network missing `node-network/delete`, and delete nonexistent

## Ranging — `scenarios/08_ranging.md`

- [x] RANGE-01 — report ranging measurement success (required switching to fresh never-`PATCH`ed nodes to avoid NODE-32; see scenario doc)
- [x] RANGE-02 — report with `reported_by_device_id` not matching the source node
- [x] RANGE-03 — report referencing an unapproved node
- [x] RANGE-04 — report with unknown pan_id
- [x] RANGE-05 — report with unknown address on a valid network
- [x] RANGE-06 — report with negative distance
- [x] RANGE-07 — report with address out of uwb range
- [x] RANGE-08 — report missing `ranging/manage`
- [x] RANGE-09 — list ranging records by interval
- [x] RANGE-10 — list ranging records `start == end` (allowed boundary)
- [x] RANGE-11 — list ranging records `start > end`
- [x] RANGE-12 — list ranging records missing required `start`/`end`
- [x] RANGE-13 — list ranging records filtered by network_id/node_id
- [x] RANGE-14 — get latest ranging record
- [x] RANGE-15 — get latest ranging record when none match (returns `null`)
- [x] RANGE-16 — delete ranging records by interval
- [x] RANGE-17 — a deleted node leaves ranging records with a dangling Link, crashing list/latest reads — **BUG FOUND, FIXED** (discovered during regression testing after fixing NODE-32, which had been masking it): `_find_with_links` now omits unresolvable records instead of crashing — see scenario doc

## RangingSchedulerConfig — `scenarios/09_ranging_scheduler_config.md`

- [x] RSC-01 — get config reflects env defaults
- [x] RSC-02 — get config missing `ranging-scheduler-config/view`
- [x] RSC-03 — get config no auth
- [x] RSC-04 — patch a single field
- [x] RSC-05 — get config immediately after patch reflects the update (cache freshness)
- [x] RSC-06 — patch multiple fields at once (partial-update semantics)
- [x] RSC-07 — patch with value `0` (rejected, `gt=0`)
- [x] RSC-08 — patch with a negative value
- [x] RSC-09 — patch with an unknown extra field
- [x] RSC-10 — patch missing `ranging-scheduler-config/manage`
- [x] RSC-11 — reset to default reverts ALL fields
- [x] RSC-12 — reset missing `ranging-scheduler-config/manage`

## Cross-cutting — `scenarios/10_cross_cutting.md`

- [x] XCUT-01 — missing bearer token on a protected route
- [x] XCUT-02 — malformed/garbage bearer token
- [x] XCUT-03 — expired access token
- [x] XCUT-04 — tampered token signature
- [x] XCUT-05 — refresh token used where an access token is expected — **BUG FOUND, FIXED**: distinct secrets (AUTH-09 fix) + `KeyError` now converts to `InvalidTokenDomainException`; returns a clean `401` — see scenario doc
- [x] XCUT-06 — pagination boundary `limit=101`
- [x] XCUT-07 — pagination boundary `limit=0` and `page=-1`
- [x] XCUT-08 — malformed non-ObjectId-shaped path id — **BUG FOUND, FIXED**: new `get_by_id` helper returns `None` for invalid id shapes instead of crashing; now returns `404` across every affected entity — see scenario doc
- [x] XCUT-09 — unknown extra field on a representative `extra=forbid` DTO
- [x] XCUT-10 — malformed JSON body
- [x] XCUT-11 — unsupported HTTP method on a valid path
- [x] XCUT-12 — nonexistent path
- [x] XCUT-13 — public docs routes reachable with zero auth
- [x] XCUT-14 — every other route requires the bearer token even for otherwise-public-seeming actions

---

**Total: 193 scenarios** — 23 auth + 29 user + 23 role (+ROLE-23) + 15 permission (+PERM-15) + 32 node (+NODE-32) + 14 node-websocket + 14 node-network + 17 ranging (+RANGE-17) + 12 ranging-scheduler-config + 14 cross-cutting.
