import re
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, List, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from ips_app.adapters.driving.http.dto.common import ErrorResponse
from ips_app.adapters.driving.http.middleware.auth_jwt import get_claims

Rule = Callable[[Request], Awaitable[Optional[JSONResponse]]]

@dataclass
class RouteRule:
    path_pattern: str
    methods: List[str]
    rules: Dict[str, Rule]
    _compiled: re.Pattern = field(init=False, repr=False)

    def __post_init__(self):
        pattern = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", self.path_pattern)
        self._compiled = re.compile(f"^{pattern}$")

    def match(self, path: str, method: str) -> Optional[Dict[str, str]]:
        if method.upper() not in [m.upper() for m in self.methods]:
            return None
        m = self._compiled.match(path)
        if m is None:
            return None
        return m.groupdict()

class RoleRuleMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        route_rules: List[RouteRule] = [],
    ):
        super().__init__(app)
        self.route_rules = route_rules

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        for route_rule in self.route_rules:
            path_params = route_rule.match(path, method)
            if path_params is None:
                continue

            request.state.path_params = path_params

            claims = get_claims(request)
            if claims is None:
                return JSONResponse(status_code=401, content=ErrorResponse(error="Unauthorized").model_dump())

            rule = route_rule.rules.get(claims.role_id)
            if rule is None:
                return JSONResponse(status_code=403, content=ErrorResponse(error="Forbidden").model_dump())

            result = await rule(request)
            if result is not None:
                return result

            break

        return await call_next(request)

async def rule_allow_all(_: Request) -> None:
    pass

def rule_claims_user_id_equals_path(param_name: str = "user_id") -> Rule:
    async def rule(request: Request) -> Optional[JSONResponse]:
        claims = get_claims(request)
        path_params = getattr(request.state, "path_params", {})
        path_user_id = path_params.get(param_name, "")
        if not claims or str(claims.user_id) != str(path_user_id):
            return JSONResponse(status_code=403, content=ErrorResponse(error="Access denied").model_dump())
        return None
    return rule

def rule_claims_role_id_equals_path(param_name: str = "role_id") -> Rule:
    async def rule(request: Request) -> Optional[JSONResponse]:
        claims = get_claims(request)
        path_params = getattr(request.state, "path_params", {})
        path_role_id = path_params.get(param_name, "")
        if not claims or str(claims.role_id) != str(path_role_id):
            return JSONResponse(status_code=403, content=ErrorResponse(error="Access denied").model_dump())
        return None
    return rule
