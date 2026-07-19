# API Test Checklist — v1.0.0-dev.1

189 scenarios across 8 entities, the node websocket protocol, and cross-cutting concerns. Full request/response detail, curl/Python snippets, and preconditions for every item live in `scenarios/*.md` — this file is the skimmable master list. See `scenarios/00_environment_and_setup.md` before running anything (deployment, seeded accounts, token-expiry caveat).

Check a box only once the scenario has actually been run against a deployed instance and the observed result matches (or once a discovered discrepancy has been noted inline).

## Auth — `scenarios/01_auth.md`

- [ ] AUTH-01 — sign-in success
- [ ] AUTH-02 — sign-in wrong password
- [ ] AUTH-03 — sign-in unknown username
- [ ] AUTH-04 — sign-in empty username/password
- [ ] AUTH-05 — sign-in as a suspended user
- [ ] AUTH-06 — sign-in as a banned user
- [ ] AUTH-07 — refresh-token success
- [ ] AUTH-08 — refresh-token expired (documents why this is impractical to test directly; see XCUT-03 for the equivalent access-token expiry test)
- [ ] AUTH-09 — refresh-token with an access token instead
- [ ] AUTH-10 — refresh-token malformed string
- [ ] AUTH-11 — register success
- [ ] AUTH-12 — register without `auth/manage` permission
- [ ] AUTH-13 — register duplicate username
- [ ] AUTH-14 — register with invalid `role_id`
- [ ] AUTH-15 — register with weak password (< 8 chars)
- [ ] AUTH-16 — register with invalid username (starts with non-alnum)
- [ ] AUTH-17 — change-own-password success
- [ ] AUTH-18 — change-own-password wrong old password
- [ ] AUTH-19 — change-own-password weak new password
- [ ] AUTH-20 — change-own-password no auth
- [ ] AUTH-21 — admin reset-password success
- [ ] AUTH-22 — admin reset-password missing `auth/manage`
- [ ] AUTH-23 — admin reset-password nonexistent user_id

## User — `scenarios/02_user.md`

- [ ] USER-01 — get own profile
- [ ] USER-02 — get own profile no auth
- [ ] USER-03 — get own permissions
- [ ] USER-04 — get own permissions as `user` (zero permissions)
- [ ] USER-05 — update own info success
- [ ] USER-06 — update own info invalid name (below 2-char minimum)
- [ ] USER-07 — update own info invalid username (consecutive dots)
- [ ] USER-08 — update own bio too long (> 2000 chars)
- [ ] USER-09 — update own preferences success
- [ ] USER-10 — update own preferences non-object value
- [ ] USER-11 — list users default pagination
- [ ] USER-12 — list users `limit=101` (over max)
- [ ] USER-13 — list users `limit=0`
- [ ] USER-14 — list users `page=-1`
- [ ] USER-15 — list users search no match
- [ ] USER-16 — list users filtered by `role_id`/`status`
- [ ] USER-17 — list users missing `user/view`
- [ ] USER-18 — get user by id
- [ ] USER-19 — get user by id not found
- [ ] USER-20 — get user permissions by id
- [ ] USER-21 — admin update user role
- [ ] USER-22 — admin update user role with invalid role_id
- [ ] USER-23 — admin update user status (valid enum)
- [ ] USER-24 — admin update user status invalid enum value
- [ ] USER-25 — admin update info/preferences/role/status without `user/manage`
- [ ] USER-26 — delete user success
- [ ] USER-27 — delete user missing `user/delete`
- [ ] USER-28 — delete nonexistent user
- [ ] USER-29 — admin deletes their own currently-authenticated account

## Role — `scenarios/03_role.md`

- [ ] ROLE-01 — create role success
- [ ] ROLE-02 — create role duplicate name
- [ ] ROLE-03 — create role invalid resource-name (starts with non-alnum)
- [ ] ROLE-04 — create role missing `role/manage`
- [ ] ROLE-05 — list roles
- [ ] ROLE-06 — get default role
- [ ] ROLE-07 — get role by id
- [ ] ROLE-08 — get role by id not found
- [ ] ROLE-09 — get role permissions
- [ ] ROLE-10 — update role name/description
- [ ] ROLE-11 — `PATCH /roles/{id}/default` unsets the previous default
- [ ] ROLE-12 — update role preferences non-object
- [ ] ROLE-13 — add permissions to role (incl. idempotent re-add)
- [ ] ROLE-14 — add permissions empty list
- [ ] ROLE-15 — add permissions with a nonexistent id in the list
- [ ] ROLE-16 — remove permissions from role
- [ ] ROLE-17 — add/remove permissions missing `role/manage`
- [ ] ROLE-18 — delete role success
- [ ] ROLE-19 — delete role currently assigned to a user
- [ ] ROLE-20 — delete role missing `role/delete`
- [ ] ROLE-21 — delete nonexistent role
- [ ] ROLE-22 — delete the seeded default role (documents the two possible branches; not to be run destructively on a kept environment)

## Permission — `scenarios/04_permission.md`

- [ ] PERM-01 — create permission success
- [ ] PERM-02 — create permission duplicate name
- [ ] PERM-03 — create permission invalid resource-name
- [ ] PERM-04 — create permission missing `permission/manage`
- [ ] PERM-05 — list permissions
- [ ] PERM-06 — list permissions search
- [ ] PERM-07 — list permissions missing `permission/view`
- [ ] PERM-08 — get permission by id
- [ ] PERM-09 — get permission by id not found
- [ ] PERM-10 — update permission name/description
- [ ] PERM-11 — update permission preferences non-object
- [ ] PERM-12 — delete permission success
- [ ] PERM-13 — delete permission currently attached to a role
- [ ] PERM-14 — delete permission missing `permission/delete`, and delete nonexistent

## Node — `scenarios/05_node.md`

- [ ] NODE-01 — create node success
- [ ] NODE-02 — create node duplicate device_id
- [ ] NODE-03 — create node with `network_id` but no `address` (XOR violation)
- [ ] NODE-04 — create node with address out of range
- [ ] NODE-05 — create node with a valid network+address assignment
- [ ] NODE-06 — create node with invalid name
- [ ] NODE-07 — create node missing `node/manage`
- [ ] NODE-08 — list nodes with all filters
- [ ] NODE-09 — list nodes pagination boundaries
- [ ] NODE-10 — get registered device ids (none connected)
- [ ] NODE-11 — get registration status for a device_id (not connected)
- [ ] NODE-12 — get registration status while connected
- [ ] NODE-13 — get node by device_id
- [ ] NODE-14 — get node by device_id not found
- [ ] NODE-15 — get node by network+address
- [ ] NODE-16 — get node by network+address not found
- [ ] NODE-17 — restart a not-approved node
- [ ] NODE-18 — restart an approved but not-connected node
- [ ] NODE-19 — restart an approved and connected node
- [ ] NODE-20 — get node by id not found
- [ ] NODE-21 — update node info
- [ ] NODE-22 — update node network assignment — reassign to a different address
- [ ] NODE-23 — update node network assignment — unassign both to null
- [ ] NODE-24 — update node network assignment XOR violation
- [ ] NODE-25 — update node network assignment to an address already taken
- [ ] NODE-26 — update node status — approve a pending node
- [ ] NODE-27 — update node status invalid enum value
- [ ] NODE-28 — update node preferences non-object
- [ ] NODE-29 — delete node success
- [ ] NODE-30 — delete a currently-connected node
- [ ] NODE-31 — delete nonexistent node

## Node Websocket — `scenarios/06_node_websocket.md`

- [ ] NODE-WS-01 — connect with a brand-new device_id → auto-registers pending → rejected (1008)
- [ ] NODE-WS-02 — approve, then reconnect → accepted
- [ ] NODE-WS-03 — second connection for the same device_id evicts the first (old closed 1000)
- [ ] NODE-WS-04 — graceful client-initiated disconnect
- [ ] NODE-WS-05 — heartbeat event → connection stays open, no-op
- [ ] NODE-WS-06 — ack event → connection stays open, no-op
- [ ] NODE-WS-07 — unrecognized message shape → connection closed (1008)
- [ ] NODE-WS-08 — invalid JSON text → connection closed (1008)
- [ ] NODE-WS-09 — JSON array instead of object → connection closed (1008)
- [ ] NODE-WS-10 — valid ranging message → connection stays open even if the measurement is rejected
- [ ] NODE-WS-11 — ranging message missing a required data key → connection closed (1011, discovered inconsistency vs. NODE-WS-10)
- [ ] NODE-WS-12 — `label:"error"` → no-op
- [ ] NODE-WS-13 — `WebSocketDisconnect` mid-loop handled silently
- [ ] NODE-WS-14 — server→node RESTART command payload verification (cross-ref NODE-19)

## NodeNetwork — `scenarios/07_node_network.md`

- [ ] NETNET-01 — create node network success
- [ ] NETNET-02 — create node network duplicate pan_id
- [ ] NETNET-03 — create node network pan_id out of range
- [ ] NETNET-04 — create node network invalid name
- [ ] NETNET-05 — create node network missing `node-network/manage`
- [ ] NETNET-06 — list node networks
- [ ] NETNET-07 — get node network by pan_id
- [ ] NETNET-08 — get node network by pan_id not found
- [ ] NETNET-09 — get node network by id not found
- [ ] NETNET-10 — update node network name/description
- [ ] NETNET-11 — update node network to an already-taken pan_id
- [ ] NETNET-12 — delete node network success
- [ ] NETNET-13 — delete node network still referenced by a node
- [ ] NETNET-14 — delete node network missing `node-network/delete`, and delete nonexistent

## Ranging — `scenarios/08_ranging.md`

- [ ] RANGE-01 — report ranging measurement success
- [ ] RANGE-02 — report with `reported_by_device_id` not matching the source node
- [ ] RANGE-03 — report referencing an unapproved node
- [ ] RANGE-04 — report with unknown pan_id
- [ ] RANGE-05 — report with unknown address on a valid network
- [ ] RANGE-06 — report with negative distance
- [ ] RANGE-07 — report with address out of uwb range
- [ ] RANGE-08 — report missing `ranging/manage`
- [ ] RANGE-09 — list ranging records by interval
- [ ] RANGE-10 — list ranging records `start == end` (allowed boundary)
- [ ] RANGE-11 — list ranging records `start > end`
- [ ] RANGE-12 — list ranging records missing required `start`/`end`
- [ ] RANGE-13 — list ranging records filtered by network_id/node_id
- [ ] RANGE-14 — get latest ranging record
- [ ] RANGE-15 — get latest ranging record when none match (returns `null`)
- [ ] RANGE-16 — delete ranging records by interval

## RangingSchedulerConfig — `scenarios/09_ranging_scheduler_config.md`

- [ ] RSC-01 — get config reflects env defaults
- [ ] RSC-02 — get config missing `ranging-scheduler-config/view`
- [ ] RSC-03 — get config no auth
- [ ] RSC-04 — patch a single field
- [ ] RSC-05 — get config immediately after patch reflects the update (cache freshness)
- [ ] RSC-06 — patch multiple fields at once (partial-update semantics)
- [ ] RSC-07 — patch with value `0` (rejected, `gt=0`)
- [ ] RSC-08 — patch with a negative value
- [ ] RSC-09 — patch with an unknown extra field
- [ ] RSC-10 — patch missing `ranging-scheduler-config/manage`
- [ ] RSC-11 — reset to default reverts ALL fields
- [ ] RSC-12 — reset missing `ranging-scheduler-config/manage`

## Cross-cutting — `scenarios/10_cross_cutting.md`

- [ ] XCUT-01 — missing bearer token on a protected route
- [ ] XCUT-02 — malformed/garbage bearer token
- [ ] XCUT-03 — expired access token
- [ ] XCUT-04 — tampered token signature
- [ ] XCUT-05 — refresh token used where an access token is expected
- [ ] XCUT-06 — pagination boundary `limit=101`
- [ ] XCUT-07 — pagination boundary `limit=0` and `page=-1`
- [ ] XCUT-08 — malformed non-ObjectId-shaped path id → confirmed `500` (documented gap, not a false assumption)
- [ ] XCUT-09 — unknown extra field on a representative `extra=forbid` DTO
- [ ] XCUT-10 — malformed JSON body
- [ ] XCUT-11 — unsupported HTTP method on a valid path
- [ ] XCUT-12 — nonexistent path
- [ ] XCUT-13 — public docs routes reachable with zero auth
- [ ] XCUT-14 — every other route requires the bearer token even for otherwise-public-seeming actions

---

**Total: 189 scenarios** — 23 auth + 29 user + 22 role + 14 permission + 31 node + 14 node-websocket + 14 node-network + 16 ranging + 12 ranging-scheduler-config + 14 cross-cutting.
