# Cross-cutting concerns

Behaviors that belong to the JWT middleware, FastAPI/pydantic validation layer, or Beanie/Mongo id-handling — not owned by any single entity. Exercised against a couple of representative routes rather than every single endpoint, since the mechanism is identical everywhere.

**Fixtures needed**: `$ADMIN_TOKEN`.

---

### XCUT-01: missing bearer token on a protected route
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/permissions
```
**Expected**: `401` — rejected by `JwtMiddleware` before the route (and its `permission_check` dependency) ever runs.

### XCUT-02: malformed/garbage bearer token
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/permissions -H 'Authorization: Bearer not-a-real-token'
```
**Expected**: `401` (`InvalidTokenDomainException` inside `JwtMiddleware`, message `"Your session is invalid. Please sign in again."`).

### XCUT-03: expired access token
```bash
ADMIN_TOKEN=$(curl -s -X POST http://localhost:50002/auth/sign-in -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"CHANGE_ME"}' | jq -r .access_token)
sleep 65
curl -s -w '\n%{http_code}' http://localhost:50002/permissions -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `401`, message `"Your session has expired. Please sign in again."` (`ExpiredTokenDomainException`, since `.env`'s `APP_ACCESS_TOKEN_EXPIRY=1m`).

### XCUT-04: tampered token signature
```bash
GOOD=$(curl -s -X POST http://localhost:50002/auth/sign-in -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"CHANGE_ME"}' | jq -r .access_token)
TAMPERED="${GOOD%?}X"   # flip the last character
curl -s -w '\n%{http_code}' http://localhost:50002/permissions -H "Authorization: Bearer $TAMPERED"
```
**Expected**: `401` (`InvalidTokenDomainException` — signature no longer verifies).

### XCUT-05: refresh token used where an access token is expected
```bash
REFRESH=$(curl -s -X POST http://localhost:50002/auth/sign-in -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"CHANGE_ME"}' | jq -r .refresh_token)
curl -s -w '\n%{http_code}' http://localhost:50002/permissions -H "Authorization: Bearer $REFRESH"
```
**Expected**: `401` — access and refresh tokens are signed with different secrets (`APP_ACCESS_TOKEN_SECRET` vs `APP_REFRESH_TOKEN_SECRET`), so a refresh token fails signature verification when checked against the access secret.

### XCUT-06: pagination boundary — `limit=101`
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/permissions?limit=101" -H "Authorization: Bearer $ADMIN_TOKEN"
curl -s -w '\n%{http_code}' "http://localhost:50002/roles?limit=101" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: both `422` (`le=100` on the shared `Query` pattern).

### XCUT-07: pagination boundary — `limit=0` and `page=-1`
```bash
curl -s -w '\n%{http_code}' "http://localhost:50002/permissions?limit=0" -H "Authorization: Bearer $ADMIN_TOKEN"
curl -s -w '\n%{http_code}' "http://localhost:50002/permissions?page=-1" -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: both `422`.

### XCUT-08: malformed, non-ObjectId-shaped path id → confirmed `500`, not `404`
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/permissions/not-an-id -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `500` (`UnexpectedDomainException`). **This was verified directly against the code, not assumed**: every repository's `read_*_by_id`-style method calls `to_object_id(id)` (`infrastructure/repository/_shared/object_id.py`) first, which only converts a string to a `PydanticObjectId` if `PydanticObjectId.is_valid(value)` — for an invalid shape like `"not-an-id"` it returns the **string unchanged**. That string is then passed to Beanie's `Document.get(document_id)`, whose implementation (`beanie/odm/documents.py`) calls `parse_object_as(PydanticObjectId, document_id)` whenever the value isn't already a `PydanticObjectId` instance — this raises a pydantic validation error for a malformed id, which is **not** a `DomainException`, so it's caught by the repository's generic `except Exception as e: raise UnexpectedDomainException(str(e)) from e` and surfaces as HTTP `500`. This applies to every entity's `GET/PATCH/DELETE /{id}`-style route (`permissions`, `roles`, `users`, `nodes`, `node-networks`) — worth flagging as a real gap: a client typo in an id currently produces a `500` instead of a `400`/`404`, and it would be a reasonable follow-up bug to fix (e.g. validate id shape before calling `.get()`, or catch the pydantic error alongside `DomainException`), but as of this writing it is **not** fixed — document the actual behavior, don't paper over it.

### XCUT-09: unknown extra field on a representative `extra=forbid` DTO
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/permissions \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"x/y","description":"z","totally_unexpected_field":true}'
```
**Expected**: `422` (pydantic `ConfigDict(extra="forbid")`).

### XCUT-10: malformed JSON body
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/permissions \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{not valid json'
```
**Expected**: `422` (FastAPI JSON body parse failure).

### XCUT-11: unsupported HTTP method on a valid path
```bash
curl -s -w '\n%{http_code}' -X PUT http://localhost:50002/permissions -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `405` (no `PUT` handler registered on `/permissions` — only `POST`/`GET`).

### XCUT-12: nonexistent path
```bash
curl -s -w '\n%{http_code}' http://localhost:50002/this-route-does-not-exist -H "Authorization: Bearer $ADMIN_TOKEN"
```
**Expected**: `404` (FastAPI's default "not found", not a `NotFoundDomainException`/`ErrorResponse` body — it's plain `{"detail": "Not Found"}`, worth noting the body shape differs from the app's own `ErrorResponse{error: str}` shape since this never reaches `register_exception_handlers`).

### XCUT-13: public docs routes reachable with zero auth
```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:50002/docs
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:50002/openapi.json
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:50002/redoc
```
**Expected**: all `200` — these three plus `/docs/oauth2-redirect`, `/auth/sign-in`, `/auth/refresh-token` are `JwtMiddleware`'s `excluded_paths`, reachable with no `Authorization` header at all.

### XCUT-14: every other route requires the bearer token even for otherwise-public-seeming actions
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"role_id":"000000000000000000000000","name":"X","username":"y","password":"whatever1"}'
```
**Expected**: `401` from `JwtMiddleware` itself (not from `permission_check`'s own 401 branch) — `/auth/register` is NOT in `excluded_paths`, unlike `/auth/sign-in`/`/auth/refresh-token`, so a request with no token at all never reaches the `guard_manage` dependency.
