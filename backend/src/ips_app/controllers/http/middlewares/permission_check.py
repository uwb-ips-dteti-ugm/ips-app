from collections.abc import Sequence

from fastapi import Depends, HTTPException, status

from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.models.exception import DomainException, NotFoundDomainException
from ips_app.domain.ports.driving.http.role import RoleHTTP


def permission_check(permission_names: Sequence[str], service: RoleHTTP):
    required_permissions = set(permission_names)

    async def check() -> None:
        claims = get_claims()
        if not claims:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please sign in to continue.",
            )

        if not required_permissions:
            return

        if not claims.role_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account does not have a role assigned. Please contact an administrator.",
            )

        try:
            permissions = await service.get_role_permissions(claims.role_id)
        except NotFoundDomainException as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your role could not be found. Please contact an administrator.",
            ) from e
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your permissions could not be verified. Please try again.",
            ) from e

        granted_permissions = {
            permission.name
            for permission in permissions
        }
        missing_permissions = required_permissions - granted_permissions
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

    return Depends(check)
