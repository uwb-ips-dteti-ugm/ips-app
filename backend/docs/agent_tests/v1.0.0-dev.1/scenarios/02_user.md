# User — `/users` (prefix, tag "User")

Endpoints: `GET /users/me`, `GET /users/me/permissions`, `PATCH /users/me/info`, `PATCH /users/me/preferences`, `GET /users`, `GET /users/{id}`, `GET /users/{id}/permissions`, `PATCH /users/{id}/info|preferences|role|status`, `DELETE /users/{id}`.

**Fixtures needed**: `$ADMIN_TOKEN`, `$USER_TOKEN`, and at least one throwaway user (`testperson1` from `AUTH-11`, `$TESTPERSON_ID`) to update/delete without touching the seeded accounts.

---

### USER-01: get own profile
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/users/me -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `UserResponse` with `username: "admin"`, embedded `role` object.

### USER-02: get own profile no auth
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/users/me
```
**Expected**: `401` (JWT middleware, no bearer token).

### USER-03: get own permissions
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/users/me/permissions -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `List[PermissionResponse]` of length 21 for admin.

### USER-04: get own permissions as `user` (zero permissions)
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/users/me/permissions -H "Authorization: Bearer $USER_TOKEN"
```
**Expected**: `200`, `[]` (empty list — `authorization_check()` only requires sign-in, not any specific permission).

### USER-05: update own info success
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/users/me/info \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Administrator","bio":"I run this thing."}'
```
**Expected**: `200`, `name`/`bio` updated in response.

### USER-06: update own info invalid name (1 char, below `validate_name`'s 2-char minimum)
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/users/me/info \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"A"}'
```
**Expected**: `400` (`"Name must be between 2 and 100 characters."`).

### USER-07: update own info invalid username (consecutive dots)
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/users/me/info \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"username":"ad..min"}'
```
**Expected**: `400` (`"Username must not contain consecutive dots."`). Run this on a throwaway user, not the real `admin` account, in case validation somehow partially applies before failing — safer to target `testperson1`.

### USER-08: update own bio too long (> 2000 chars)
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/users/me/info \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"bio\":\"$(python3 -c 'print("a"*2001)')\"}"
```
**Expected**: `400` (`"Bio must not exceed 2000 characters."`).

### USER-09: update own preferences success
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/users/me/preferences \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"preferences":{"theme":"dark"}}'
```
**Expected**: `200`, `preferences: {"theme":"dark"}`.

### USER-10: update own preferences non-object value
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/users/me/preferences \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"preferences":"not-an-object"}'
```
**Expected**: `422` — pydantic type validation rejects a non-`Dict` value before it ever reaches `validate_preferences`, since the field's declared type is `Dict[str, Any]`.

### USER-11: list users default pagination
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/users -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `PaginatedResponse` with `page:0, limit:20`, `items` containing at least `admin`/`user`/`testperson1`.

### USER-12: list users `limit=101` (over max)
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/users?limit=101" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `422` (FastAPI query validation, `le=100`).

### USER-13: list users `limit=0`
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/users?limit=0" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `422` (`ge=1`).

### USER-14: list users `page=-1`
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/users?page=-1" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `422` (`ge=0`).

### USER-15: list users search no match
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/users?search=zzz-nope-zzz" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"items": [], "page":0, "limit":20, "total":0}`.

### USER-16: list users filtered by `role_id`/`status`
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/users?status=active" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, only `status="active"` users returned.

### USER-17: list users missing `user/view`
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/users -H "Authorization: Bearer $USER_TOKEN"
```
**Expected**: `403`.

### USER-18: get user by id
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/users/$TESTPERSON_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`.

### USER-19: get user by id not found
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/users/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### USER-20: get user permissions by id
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/users/$TESTPERSON_ID/permissions" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, reflects `testperson1`'s role's permission set (empty, since registered with the `user` role in `AUTH-11`).

### USER-21: admin update user role
**Preconditions**: `$ADMIN_ROLE_ID` (`GET /roles?search=admin`).
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/users/$TESTPERSON_ID/role" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"role_id\":\"$ADMIN_ROLE_ID\"}"
```
**Expected**: `200`, `role.id == $ADMIN_ROLE_ID`.

### USER-22: admin update user role with invalid role_id
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/users/$TESTPERSON_ID/role" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"role_id":"000000000000000000000000"}'
```
**Expected**: `404`.

### USER-23: admin update user status (valid enum)
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/users/$TESTPERSON_ID/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"status":"suspended"}'
```
**Expected**: `200`, `status: "suspended"`. (This is the fixture `AUTH-05` needs — revert back to `"active"` afterward if reusing this account elsewhere.)

### USER-24: admin update user status invalid enum value
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/users/$TESTPERSON_ID/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"status":"disabled"}'
```
**Expected**: `422` — `"disabled"` isn't a member of `UserStatus` (`active`/`suspended`/`banned`), so pydantic enum validation rejects it before the route runs.

### USER-25: admin update info/preferences/role/status without `user/manage`
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/users/$TESTPERSON_ID/info" \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Hacker"}'
```
**Expected**: `403`.

### USER-26: delete user success
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/users/$TESTPERSON_ID" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `200`, `{"message": "User deleted successfully."}`. Confirm with a follow-up `GET` on the same id → `404`.

### USER-27: delete user missing `user/delete`
**Preconditions**: register a fresh throwaway user first (deletion is destructive), then attempt delete as `$USER_TOKEN`.
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/users/$OTHER_USER_ID" -H "Authorization: Bearer $USER_TOKEN"
```
**Expected**: `403`.

### USER-28: delete nonexistent user
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/users/000000000000000000000000" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404`.

### USER-29: admin deletes their own currently-authenticated account
**Preconditions**: create a second admin-role account first (e.g. via `AUTH-11` with the admin role id), sign in as it to get a second admin token, then have that account delete itself.
```bash
curl -s -w '\n%{http_code}' -X DELETE "http://localhost:50002/users/$SECOND_ADMIN_ID" -H "Authorization: Bearer $SECOND_ADMIN_TOKEN"
```
**Expected**: nothing in `delete_user` (`application/user/user.py`) special-cases self-deletion, so this is expected to succeed with `200` — worth confirming explicitly rather than assuming, since a self-delete-while-authenticated edge case is easy to silently leave unguarded. Also confirm the already-issued access token for that account is NOT proactively revoked (there is no token-blocklist/revocation mechanism in this codebase — `JwtMiddleware` only checks the JWT signature/expiry, never DB existence). A follow-up `GET /users/me` with the same still-valid token should pass JWT validation but then fail with `404`, since `UserHandler.get_me` → `UserUsecase.get_user_by_id(claims.user_id)` → `repo.read_user_by_id` re-reads from Mongo and raises `NotFoundDomainException` for the now-deleted document.
