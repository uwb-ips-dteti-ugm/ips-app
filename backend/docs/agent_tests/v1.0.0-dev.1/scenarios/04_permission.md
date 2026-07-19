# Permission — `/permissions` (prefix, tag "Permission")

Endpoints: `POST /permissions`, `GET /permissions`, `GET /permissions/{id}`, `PATCH /permissions/{id}`, `PATCH /permissions/{id}/preferences`, `DELETE /permissions/{id}`.

**Fixtures needed**: `$ADMIN_TOKEN`, `$USER_TOKEN`.

---

### PERM-01: create permission success
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/permissions \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"widget/manage","description":"Manage widgets"}'
```
**Expected**: `200`, `PermissionResponse` echoing `name`/`description`.

### PERM-02: create permission duplicate name
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/permissions \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"widget/manage","description":"dup"}'
```
**Expected**: `409` (unique index on `PermissionDocument.name`).

### PERM-03: create permission invalid resource-name (contains an illegal char, e.g. `@`)
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/permissions \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"widget@bad","description":"x"}'
```
**Expected**: `400` (`validate_resource_name`).

### PERM-04: create permission missing `permission/manage`
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/permissions \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"whatever/manage","description":"x"}'
```
**Expected**: `403`.

### PERM-05: list permissions
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/permissions -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, includes all 21 seeded permissions plus `widget/manage`.

### PERM-06: list permissions search
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/permissions?search=widget" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, only `widget/manage` in `items`, `total:1`.

### PERM-07: list permissions missing `permission/view`
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/permissions -H "Authorization: Bearer $USER_TOKEN"
```
**Expected**: `403`.

### PERM-08: get permission by id
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/permissions/$WIDGET_PERMISSION_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`.

### PERM-09: get permission by id not found
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/permissions/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### PERM-10: update permission name/description
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/permissions/$WIDGET_PERMISSION_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"description":"Manage all the widgets"}'
```
**Expected**: `200`.

### PERM-11: update permission preferences non-object
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/permissions/$WIDGET_PERMISSION_ID/preferences" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"preferences":123}'
```
**Expected**: `422` (pydantic `Dict[str,Any]` type check).

### PERM-12: delete permission success
**Preconditions**: `widget/manage` is not attached to any role (never ran `ROLE-13` against it, or ran `ROLE-16` to detach it first).
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/permissions/$WIDGET_PERMISSION_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"message": "Permission deleted successfully."}`.

### PERM-13: delete permission currently attached to a role
**Preconditions**: create a fresh permission, attach it to a role via `POST /roles/{id}/permissions`.
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/permissions/$ATTACHED_PERMISSION_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `403` — `infrastructure/repository/permission/beanie.py:delete_permission_by_id` checks `RoleDocument.find_one(...)` for any role still linking this permission and raises `ForbiddenDomainException("Permission is used by a role.")` if found (confirmed by reading the repository source, not assumed). To actually delete it, detach from every role first (`DELETE /roles/{id}/permissions`), then retry.

### PERM-14: delete permission missing `permission/delete`, and delete nonexistent
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/permissions/$WIDGET_PERMISSION_ID" -H "Authorization: Bearer $USER_TOKEN"
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/permissions/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: first call `403`; second call `404`.
