# RangingSchedulerConfig — `/ranging-scheduler-config` (prefix, tag "RangingSchedulerConfig")

Endpoints: `GET /ranging-scheduler-config`, `PATCH /ranging-scheduler-config`, `POST /ranging-scheduler-config/reset`. Singleton config — no create/delete/pagination. `guard_view` = `ranging-scheduler-config/view`, `guard_manage` = `ranging-scheduler-config/manage` (applies to both `PATCH` and `POST /reset`).

The cache is loaded once at process startup from the DB (seeded on first run) and refreshed in-memory on every successful update — see `AGENTS.md` §9 for the full design. This means `GET` right after a `PATCH` must reflect the change with no propagation delay; if it doesn't, that's a real bug, not eventual consistency to tolerate.

**Fixtures needed**: `$ADMIN_TOKEN`, `$USER_TOKEN`. Env defaults (from `.env` in this deployment): `listen_timeout_uus=120000`, `initiate_timeout_uus=12000`, `listen_to_initiate_delay_ms=80`, `pair_delay_ms=80`, `idle_delay_ms=250`.

---

### RSC-01: get config reflects env defaults
**Preconditions**: freshly seeded DB, no prior `PATCH`/`reset` in this run.
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/ranging-scheduler-config -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, all five fields match the defaults listed above.

### RSC-02: get config missing `ranging-scheduler-config/view`
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/ranging-scheduler-config -H "Authorization: Bearer $USER_TOKEN"
```
**Expected**: `403`.

### RSC-03: get config no auth
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/ranging-scheduler-config
```
**Expected**: `401`.

### RSC-04: patch a single field
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/ranging-scheduler-config \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"idle_delay_ms":500}'
```
**Expected**: `200`, `idle_delay_ms:500`, every other field unchanged from `RSC-01`.

### RSC-05: get config immediately after patch reflects the update (cache freshness)
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/ranging-scheduler-config -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `idle_delay_ms:500` — confirms the in-memory cache was refreshed synchronously by `RSC-04`, not just the DB document.

### RSC-06: patch multiple fields at once
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/ranging-scheduler-config \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"listen_timeout_uus":150000,"pair_delay_ms":100}'
```
**Expected**: `200`, both fields updated, `idle_delay_ms` still `500` from `RSC-04` (partial update semantics — untouched fields are preserved, not reset).

### RSC-07: patch with value `0` (rejected — `gt=0`, not `ge=0`)
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/ranging-scheduler-config \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"idle_delay_ms":0}'
```
**Expected**: `422` (pydantic `Field(gt=0)` — `0` itself is invalid, unlike the `ge=0` pattern used elsewhere in this API).

### RSC-08: patch with a negative value
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/ranging-scheduler-config \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"pair_delay_ms":-10}'
```
**Expected**: `422`.

### RSC-09: patch with an unknown extra field
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/ranging-scheduler-config \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"idle_delay_ms":300,"bogus_field":1}'
```
**Expected**: `422` (`extra="forbid"` on `UpdateRangingSchedulerConfigRequest`).

### RSC-10: patch missing `ranging-scheduler-config/manage`
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/ranging-scheduler-config \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"idle_delay_ms":300}'
```
**Expected**: `403`.

### RSC-11: reset to default reverts ALL fields, not just previously-modified ones
**Preconditions**: `RSC-04`/`RSC-06` have modified `idle_delay_ms`, `listen_timeout_uus`, `pair_delay_ms` away from defaults.
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging-scheduler-config/reset -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, all five fields back to the exact defaults from `RSC-01` (`120000/12000/80/80/250`) — confirms `reset_config_to_default` writes every field, not a partial merge of "fields that were touched."

### RSC-12: reset missing `ranging-scheduler-config/manage`
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/ranging-scheduler-config/reset -H "Authorization: Bearer $USER_TOKEN"
```
**Expected**: `403`.
