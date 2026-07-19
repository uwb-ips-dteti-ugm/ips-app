# Role — `/roles` (prefix, tag "Role")

Endpoints: `POST /roles`, `GET /roles`, `GET /roles/default`, `GET /roles/{id}`, `GET /roles/{id}/permissions`, `PATCH /roles/{id}`, `PATCH /roles/{id}/default`, `PATCH /roles/{id}/preferences`, `DELETE /roles/{id}`, `POST /roles/{id}/permissions`, `DELETE /roles/{id}/permissions`.

**Fixtures needed**: `$ADMIN_TOKEN`, `$USER_TOKEN`, and at least one existing `PermissionResponse` id (`$SOME_PERMISSION_ID`, e.g. from `04_permission.md` or a seeded permission looked up via `GET /permissions?search=node`).

---

### ROLE-01: create role success
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"operator","description":"Can operate nodes"}'
```
**Expected**: `200`, `RoleResponse` with `is_default:false`, `permissions:[]`.

### ROLE-02: create role duplicate name
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"operator","description":"dup"}'
```
**Expected**: `409` (`DuplicateDomainException`, unique index on `RoleDocument.name`).

### ROLE-03: create role invalid resource-name (starts with non-alnum)
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"-bad","description":"x"}'
```
**Expected**: `400` (`validate_resource_name`, must start with alphanumeric).

### ROLE-04: create role missing `role/manage`
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/roles \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"whatever","description":"x"}'
```
**Expected**: `403`.

### ROLE-05: list roles
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/roles -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, includes seeded `admin`/`user` roles plus `operator`.

### ROLE-06: get default role
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/roles/default -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `name:"user"`, `is_default:true` (the seeded default).

### ROLE-07: get role by id
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/roles/$OPERATOR_ROLE_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`.

### ROLE-08: get role by id not found
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/roles/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### ROLE-09: get role permissions
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/roles/$OPERATOR_ROLE_ID/permissions" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `[]` (no permissions attached yet).

### ROLE-10: update role name/description
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/roles/$OPERATOR_ROLE_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"description":"Can operate and view nodes"}'
```
**Expected**: `200`, `name` unchanged, `description` updated.

### ROLE-11: `PATCH /roles/{id}/default` unsets the previous default
**Preconditions**: `ROLE-06` confirmed `user` is currently default.
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/roles/$OPERATOR_ROLE_ID/default" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
curl -s http://localhost:50002/roles/default -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.id, .is_default'
curl -s "http://localhost:50002/roles/$USER_ROLE_ID" -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.is_default'
```
**Expected**: first call `200`, `operator.is_default:true`; second call's `GET /roles/default` now returns `operator`; third call confirms the `user` role's `is_default` flipped to `false` — this is a real cross-document side effect (`update_role_is_default_by_id` in `infrastructure/repository/role/beanie.py`), not just a local field update, so it's worth asserting both sides, not just the response of the `PATCH` call itself. **Revert** by re-running `PATCH /roles/$USER_ROLE_ID/default` afterward so later scenarios that assume `user` is default aren't broken.

### ROLE-12: update role preferences non-object
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/roles/$OPERATOR_ROLE_ID/preferences" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"preferences":"nope"}'
```
**Expected**: `422` (pydantic `Dict[str,Any]` type check).

### ROLE-13: add permissions to role
```bash
curl -s -w '\n%{http_code}' -X POST "http://localhost:50002/roles/$OPERATOR_ROLE_ID/permissions" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"permission_ids\":[\"$SOME_PERMISSION_ID\"]}"
```
**Expected**: `200`, `permissions` now includes that permission. Adding the same id again (idempotency check) should not duplicate it — re-run and confirm `permissions` length is unchanged.

### ROLE-14: add permissions empty list
```bash
curl -s -w '\n%{http_code}' -X POST "http://localhost:50002/roles/$OPERATOR_ROLE_ID/permissions" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"permission_ids":[]}'
```
**Expected**: `400` (`validate_ids_list`, `"'permission_ids' must not be empty."`).

### ROLE-15: add permissions with a nonexistent id in the list
```bash
curl -s -w '\n%{http_code}' -X POST "http://localhost:50002/roles/$OPERATOR_ROLE_ID/permissions" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"permission_ids":["000000000000000000000000"]}'
```
**Expected**: `404` — `infrastructure/repository/role/beanie.py:_read_permission_documents` explicitly checks every requested id was found and raises `NotFoundDomainException(f"Permissions not found: ...")` listing the missing ones if not; this rejects the WHOLE batch (no partial-add) if even one id in the list doesn't exist.

### ROLE-16: remove permissions from role
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/roles/$OPERATOR_ROLE_ID/permissions" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"permission_ids\":[\"$SOME_PERMISSION_ID\"]}"
```
**Expected**: `200`, `permissions` no longer includes it. Note this is a `DELETE` request with a JSON body — confirm your HTTP client sends it correctly (`curl -X DELETE -d ...` does).

### ROLE-17: add/remove permissions missing `role/manage`
```bash
curl -s -w '\n%{http_code}' -X POST "http://localhost:50002/roles/$OPERATOR_ROLE_ID/permissions" \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"permission_ids\":[\"$SOME_PERMISSION_ID\"]}"
```
**Expected**: `403`.

### ROLE-18: delete role success
**Preconditions**: `operator` role has no users assigned (confirm via `GET /users?role_id=$OPERATOR_ROLE_ID` returns empty).
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/roles/$OPERATOR_ROLE_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"message": "Role deleted successfully."}`.

### ROLE-19: delete role currently assigned to a user
**Preconditions**: create a fresh role (e.g. `"temp-role"`), assign it to a throwaway user via `PATCH /users/{id}/role`.
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/roles/$TEMP_ROLE_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `403` — `infrastructure/repository/role/beanie.py:delete_role_by_id` explicitly checks `UserDocument.find_one({"role.$id": role_id})` and raises `ForbiddenDomainException("Role is used by a user.")` if any user still references it. Confirmed by reading the repository source directly (not assumed) — this is a real referential-integrity guard, not a cascading delete.

### ROLE-20: delete role missing `role/delete`
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/roles/$OPERATOR_ROLE_ID" -H "Authorization: Bearer $USER_TOKEN"
```
**Expected**: `403`.

### ROLE-21: delete nonexistent role
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/roles/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### ROLE-22: delete the seeded default role
**Preconditions**: none beyond seeded state — this checks whether `is_default=true` gets any special delete protection.
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/roles/$USER_ROLE_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `403` IF any user still has the `user` role assigned (very likely true in a freshly-seeded environment, since new registrations without an explicit role still land somewhere — but nothing in `register`/`create_user` auto-assigns the default role, so this depends entirely on whether any current user document actually references `user_role_id`; check `GET /users?role_id=$USER_ROLE_ID` first to know which branch you're actually exercising). If zero users reference it, expect `200` — deletion succeeds even though `is_default=true`, since `delete_role_by_id` has no separate check for the default flag, only for user references. **Do not actually run this against a freshly-seeded environment you intend to keep** (the seeded `user` account itself references this role, so it will almost certainly hit the `403` "used by a user" branch, not delete it) — treat this as a documentation of the two possible branches rather than a destructive step to run casually.
