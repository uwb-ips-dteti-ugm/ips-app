# Auth — `/auth` (prefix, tag "Auth")

Endpoints covered: `POST /auth/sign-in`, `POST /auth/refresh-token`, `POST /auth/register`, `PATCH /auth/me/password`, `PATCH /auth/{user_id}/password`.

**Fixtures needed**: the seeded `admin`/`user` accounts (see `00_environment_and_setup.md`). `AUTH-05`/`AUTH-06` (suspended/banned sign-in) additionally need a throwaway user whose status is flipped via `PATCH /users/{id}/status` as `admin` — create it with `AUTH-09` (register) first, or reuse any existing non-admin user.

---

### AUTH-01: sign-in success
**Endpoint**: `POST /auth/sign-in`
**Preconditions**: seeded `admin` account exists.
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/sign-in \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"CHANGE_ME"}'
```
**Expected**: `200`, body `{"access_token": "...", "refresh_token": "..."}`, both non-empty JWT strings.

### AUTH-02: sign-in wrong password
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/sign-in \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"wrong-password"}'
```
**Expected**: `401`, `{"error": "Invalid credentials provided"}` (`InvalidCredentialsDomainException`).

### AUTH-03: sign-in unknown username
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/sign-in \
  -H 'Content-Type: application/json' \
  -d '{"username":"does-not-exist","password":"whatever123"}'
```
**Expected (as originally documented)**: `401`, `{"error": "Invalid credentials provided"}` — same message as wrong-password, so username existence isn't leaked.

**ACTUALLY OBSERVED (run against a live deployment)**: `404`, `{"error": "User 'does-not-exist' not found"}`. This is a genuine username-enumeration bug, not a documentation error: `application/auth/auth.py:sign_in` calls `self.repo.read_user_by_username(username)` and lets any `DomainException` — including the repo's `NotFoundDomainException` for a missing user — propagate unchanged, instead of catching it and normalizing to `InvalidCredentialsDomainException` the way a wrong-password attempt does. A client can distinguish "no such account" (404) from "wrong password" (401) with zero rate-limiting, which leaks account existence. Worth a real fix (catch `NotFoundDomainException` in `sign_in` and re-raise as `InvalidCredentialsDomainException`), tracked here rather than silently treated as passing.

**FIXED**: `application/auth/auth.py:sign_in` now wraps `self.repo.read_user_by_username(username)` in a `try/except NotFoundDomainException: raise InvalidCredentialsDomainException() from None`. Re-verified live: unknown username now returns `401 {"error": "Invalid credentials provided"}`, identical to the wrong-password case.

### AUTH-04: sign-in empty username/password
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/sign-in \
  -H 'Content-Type: application/json' \
  -d '{"username":"","password":""}'
```
**Expected**: `400` (`validate_non_empty_string` → `ValidatorDomainException`, `"'username' must not be empty."`).

### AUTH-05: sign-in as a suspended user
**Preconditions**: a user with `status=suspended` (as admin: `PATCH /users/{id}/status` with `{"status":"suspended"}` on any non-admin test user, e.g. one created via `AUTH-09`).
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/sign-in \
  -H 'Content-Type: application/json' \
  -d '{"username":"<suspended-username>","password":"<their-password>"}'
```
**Expected**: `403`, `{"error": "User is suspended."}` (`ForbiddenDomainException`, only checked after password verifies correctly).

### AUTH-06: sign-in as a banned user
Same as `AUTH-05` but `status=banned`.
**Expected**: `403`, `{"error": "User is banned."}`.

### AUTH-07: refresh-token success
**Preconditions**: a `refresh_token` from `AUTH-01`.
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/refresh-token \
  -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}"
```
**Expected**: `200`, new `{"access_token","refresh_token"}` pair.

### AUTH-08: refresh-token expired
**Preconditions**: sign in, capture `refresh_token`, but note that `.env`'s `APP_REFRESH_TOKEN_EXPIRY=7d` — the refresh token itself does NOT expire in a practical test window. Use the **access token** as a stand-in expired-token demonstration instead: sign in, `sleep 65`, then call any protected route with the now-expired access token (this is the realistic expired-token scenario; it's cross-referenced from `XCUT-03` in `10_cross_cutting.md` to avoid duplicating the same assertion). This entry documents that a true 7-day refresh-token-expiry test is impractical to run in real time and is intentionally not exercised end-to-end — only the access-token expiry path is.
**Expected**: N/A here — see `XCUT-03`.

### AUTH-09: refresh-token with an access token instead
**Preconditions**: an `access_token` from `AUTH-01`.
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/refresh-token \
  -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$ACCESS_TOKEN\"}"
```
**Expected (by design)**: `401` (`InvalidTokenDomainException`) — access and refresh tokens are *meant* to be signed with different secrets (`APP_ACCESS_TOKEN_SECRET` vs `APP_REFRESH_TOKEN_SECRET`), so verifying an access token against the refresh secret should fail signature validation.

**ACTUALLY OBSERVED (run against a live deployment)**: `200` — a fresh access/refresh token pair is returned. Root cause is a deployment-config issue, not a code bug: this `.env` sets both `APP_ACCESS_TOKEN_SECRET=CHANGE_ME` and `APP_REFRESH_TOKEN_SECRET=CHANGE_ME` to the identical placeholder value. `JwtTokenIssuer` correctly supports independently-configured secrets (`infrastructure/utility/token/jwt.py` takes `access_secret`/`refresh_secret` as separate constructor args and decodes each token type against its own secret) — but with both env vars set to the same literal string, HS256 signature verification can't tell an access token from a refresh token, so `validate_refresh_token` happily accepts an access token (both carry a `user_id` claim, which is all `UserRefreshTokenClaims` requires). **This means the two-secret security boundary is silently defeated by the shipped `.env`/`.env.example` default** — worth flagging as a real deployment hardening gap: any production `.env` MUST set these two secrets to different, non-placeholder values, and this test is the concrete proof of what breaks if they aren't. **Confirmed conclusively**: temporarily setting `APP_REFRESH_TOKEN_SECRET` to a different value than `APP_ACCESS_TOKEN_SECRET` and restarting `backend` (no reseed needed) makes this scenario return exactly the originally-expected `401 {"error":"Invalid token"}` — proving the code itself is correct and the only issue is the shipped `.env`/`.env.example` using the same placeholder for both secrets.

**FIXED**: `.env` and `.env.example` now ship with distinct placeholders (`APP_ACCESS_TOKEN_SECRET=CHANGE_ME_ACCESS`, `APP_REFRESH_TOKEN_SECRET=CHANGE_ME_REFRESH`), plus a comment explaining why they must differ. Re-verified live: this scenario now returns `401` as originally expected.

### AUTH-10: refresh-token malformed string
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/refresh-token \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"not.a.jwt"}'
```
**Expected**: `401` (`InvalidTokenDomainException`).

### AUTH-11: register success
**Preconditions**: `$ADMIN_TOKEN`, and the `user` role's id (`GET /roles?search=user` as admin, or `GET /roles/default`).
```bash
USER_ROLE_ID=$(curl -s http://localhost:50002/roles/default -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r .id)
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/register \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"role_id\":\"$USER_ROLE_ID\",\"name\":\"Test Person\",\"username\":\"testperson1\",\"password\":\"correct-horse\"}"
```
**Expected**: `200`, `UserResponse` body with `username: "testperson1"`, `role.id` matching `$USER_ROLE_ID`.

### AUTH-12: register without `auth/manage` permission
**Preconditions**: `$USER_TOKEN` (the seeded `user` account has zero permissions).
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/register \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"role_id":"000000000000000000000000","name":"X","username":"xperson","password":"correct-horse"}'
```
**Expected**: `403`, `{"error": "Action is forbidden."}`.

### AUTH-13: register duplicate username
**Preconditions**: `testperson1` already exists (`AUTH-11`).
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/register \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"role_id\":\"$USER_ROLE_ID\",\"name\":\"Dup\",\"username\":\"testperson1\",\"password\":\"correct-horse\"}"
```
**Expected**: `409` (`DuplicateDomainException`, unique index on `UserDocument.username`).

### AUTH-14: register with invalid `role_id`
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/register \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"role_id":"000000000000000000000000","name":"X","username":"anotherperson","password":"correct-horse"}'
```
**Expected**: `404` (`NotFoundDomainException`, role lookup fails).

### AUTH-15: register with weak password (< 8 chars)
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/register \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"role_id\":\"$USER_ROLE_ID\",\"name\":\"X\",\"username\":\"weakpwperson\",\"password\":\"short1\"}"
```
**Expected**: `400` (`ValidatorDomainException`, `"Password must be between 8 and 128 characters."`).

### AUTH-16: register with invalid username (starts with non-alnum)
```bash
curl -s -w '\n%{http_code}' -X POST http://localhost:50002/auth/register \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"role_id\":\"$USER_ROLE_ID\",\"name\":\"X\",\"username\":\"_badname\",\"password\":\"correct-horse\"}"
```
**Expected**: `400` (`"Username must start and end with an alphanumeric character."`).

### AUTH-17: change-own-password success
**Preconditions**: `testperson1` (`AUTH-11`) signed in as itself → `$TESTPERSON_TOKEN`.
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/auth/me/password \
  -H "Authorization: Bearer $TESTPERSON_TOKEN" -H 'Content-Type: application/json' \
  -d '{"old_password":"correct-horse","new_password":"even-better-horse"}'
```
**Expected**: `200`, `{"message": "Password changed successfully."}`. Verify by signing in again with the new password.

### AUTH-18: change-own-password wrong old password
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/auth/me/password \
  -H "Authorization: Bearer $TESTPERSON_TOKEN" -H 'Content-Type: application/json' \
  -d '{"old_password":"totally-wrong","new_password":"another-one-1"}'
```
**Expected**: `401` (`InvalidCredentialsDomainException`).

### AUTH-19: change-own-password weak new password
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/auth/me/password \
  -H "Authorization: Bearer $TESTPERSON_TOKEN" -H 'Content-Type: application/json' \
  -d '{"old_password":"even-better-horse","new_password":"short"}'
```
**Expected**: `400` (`ValidatorDomainException`, password length).

### AUTH-20: change-own-password no auth
```bash
curl -s -w '\n%{http_code}' -X PATCH http://localhost:50002/auth/me/password \
  -H 'Content-Type: application/json' \
  -d '{"old_password":"a","new_password":"whatever1"}'
```
**Expected**: `401` — rejected by `JwtMiddleware` itself (missing bearer token), before the route's `authorization_check()` guard ever runs.

### AUTH-21: admin reset-password success
**Preconditions**: `$ADMIN_TOKEN`, `testperson1`'s id (`$TESTPERSON_ID`).
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/auth/$TESTPERSON_ID/password" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"new_password":"admin-reset-pw1"}'
```
**Expected**: `200`, `{"message": "Password reset successfully."}`. No `old_password` required. Verify by signing in as `testperson1` with the new password.

### AUTH-22: admin reset-password missing `auth/manage`
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/auth/$TESTPERSON_ID/password" \
  -H "Authorization: Bearer $USER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"new_password":"whatever-123"}'
```
**Expected**: `403`.

### AUTH-23: admin reset-password nonexistent user_id
```bash
curl -s -w '\n%{http_code}' -X PATCH "http://localhost:50002/auth/000000000000000000000000/password" \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"new_password":"whatever-123"}'
```
**Expected**: `404` (`NotFoundDomainException`).
