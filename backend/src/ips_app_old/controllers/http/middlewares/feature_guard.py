from fastapi import Depends, HTTPException, status

from ips_app_old.controllers.http.middlewares.auth_jwt import get_claims
from ips_app_old.domain.models.exception import DomainException
from ips_app_old.domain.ports.driving.http.user import UserHTTP


def feature_guard(feature_name: str, service: UserHTTP):
    async def guard() -> None:
        claims = get_claims()
        if not claims:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )

        try:
            can_access = await service.can_access_feature_by_name(
                user_id=claims.user_id,
                feature_name=feature_name,
            )
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            ) from e

        if not can_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )

    return Depends(guard)
