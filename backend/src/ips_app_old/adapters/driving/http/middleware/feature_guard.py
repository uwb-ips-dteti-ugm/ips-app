from fastapi import Depends, HTTPException
from ips_app_old.ports.driving.http.feature import FeatureHTTPPort
from ips_app_old.adapters.driving.http.middleware.auth_jwt import get_claims


def feature_guard(feature_name: str, service: FeatureHTTPPort):
    async def guard():
        claims = get_claims()
        if not claims:
            raise HTTPException(status_code=401, detail="Unauthorized")

        can_access = await service.can_access_feature_by_name(
            user_id=claims.user_id,
            feature_name=feature_name,
        )
        if not can_access:
            raise HTTPException(status_code=403, detail="Forbidden")

    return Depends(guard)
