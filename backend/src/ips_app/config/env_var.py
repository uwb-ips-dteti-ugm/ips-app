import os
from dataclasses import dataclass

from dotenv import load_dotenv

from ips_app.domain.models.exception import (
    EnvRequiredDomainException,
    ValidatorDomainException,
)


@dataclass(frozen=True)
class EnvVar:
    log_level: str
    log_style: str
    mongo_uri: str
    mongo_db: str
    access_token_secret: str
    access_token_expiry: int
    refresh_token_secret: str
    refresh_token_expiry: int
    admin_name: str
    admin_username: str
    admin_password: str
    user_state_to_away_after: int
    user_state_to_offline_after: int
    user_state_updater_cron_period: int


def load_env_var() -> EnvVar:
    load_dotenv()

    return EnvVar(
        log_level=_fallback("LOG_LEVEL", "INFO").upper(),
        log_style=_fallback("LOG_FORMAT", "basic").lower(),
        mongo_uri=_require("MONGO_URI"),
        mongo_db=_require("MONGO_DB"),
        access_token_secret=_require("ACCESS_TOKEN_SECRET"),
        access_token_expiry=_fallback_int("ACCESS_TOKEN_EXPIRY", 3600),
        refresh_token_secret=_require("REFRESH_TOKEN_SECRET"),
        refresh_token_expiry=_fallback_int("REFRESH_TOKEN_EXPIRY", 604800),
        admin_name=_fallback("ADMIN_NAME", "admin"),
        admin_username=_require("ADMIN_USERNAME"),
        admin_password=_require("ADMIN_PASSWORD"),
        user_state_to_away_after=_fallback_int(
            "USER_STATE_TO_AWAY_AFTER",
            300,
        ),
        user_state_to_offline_after=_fallback_int(
            "USER_STATE_TO_OFFLINE_AFTER",
            1200,
        ),
        user_state_updater_cron_period=_fallback_int(
            "USER_STATE_UPDATER_CRON_PERIOD",
            300,
        ),
    )


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvRequiredDomainException(key)
    return value


def _fallback(key: str, value: str) -> str:
    return os.getenv(key, value)


def _fallback_int(key: str, value: int) -> int:
    raw_value = os.getenv(key)
    if raw_value is None:
        return value
    try:
        return int(raw_value)
    except ValueError as e:
        raise ValidatorDomainException(f"Environment variable '{key}' must be an integer.") from e
