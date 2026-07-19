from typing import Sequence

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from ips_app.domain.models.exception import DomainException
from ips_app.domain.usecases.role import RoleUsecase
from ips_app.presentation.http.middlewares.auth_jwt import get_claims

bearer_scheme = HTTPBearer(auto_error=False)


def authorization_check():
    async def guard(_: str = Depends(bearer_scheme)) -> None:
        if await get_claims() is None:
            raise HTTPException(status_code=401, detail="Please sign in to continue.")

    return Depends(guard)


def permission_check(permission_names: Sequence[str], role_usecase: RoleUsecase):
    required_permissions = set(permission_names)

    async def guard(_: str = Depends(bearer_scheme)) -> None:
        claims = await get_claims()
        if claims is None:
            raise HTTPException(status_code=401, detail="Please sign in to continue.")

        try:
            permissions = await role_usecase.get_role_permissions(claims.role_id)
        except DomainException:
            raise HTTPException(status_code=403, detail="Action is forbidden.")

        granted_permissions = {permission.name for permission in permissions}
        if not required_permissions.issubset(granted_permissions):
            raise HTTPException(status_code=403, detail="Action is forbidden.")

    return Depends(guard)
