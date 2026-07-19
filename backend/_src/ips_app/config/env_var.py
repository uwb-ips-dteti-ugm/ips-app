import os
from dataclasses import dataclass

from dotenv import load_dotenv

from ips_app.domain.models.exception import (
    EnvRequiredDomainException,
    ValidatorDomainException,
)


@dataclass(frozen=True)
class EnvVar:
    port_app: int
    port_mongo: int
    log_level: str
    log_style: str
    mongo_username: str
    mongo_password: str
    mongo_uri: str
    mongo_db: str
    access_token_secret: str
    access_token_expiry: int
    refresh_token_secret: str
    refresh_token_expiry: int
    seeder_admin_name: str
    seeder_admin_username: str
    seeder_admin_password: str
    seeder_user_name: str
    seeder_user_username: str
    seeder_user_password: str
    ranging_scheduler_listen_timeout_uus: int
    ranging_scheduler_initiate_timeout_uus: int
    ranging_scheduler_listen_to_initiate_delay_ms: int
    ranging_scheduler_pair_delay_ms: int
    ranging_scheduler_idle_delay_ms: int


def load_env_var() -> EnvVar:
    load_dotenv()

    return EnvVar(
        port_app=_fallback_int("PORT_APP", 8000),
        port_mongo=_fallback_int("PORT_MONGO", 27017),
        log_level=_fallback("LOG_LEVEL", "INFO").upper(),
        log_style=_fallback("LOG_FORMAT", "json").lower(),
        mongo_username=_require("MONGO_USERNAME"),
        mongo_password=_require("MONGO_PASSWORD"),
        mongo_uri=_require("MONGO_URI"),
        mongo_db=_require("MONGO_DB"),
        access_token_secret=_require("ACCESS_TOKEN_SECRET"),
        access_token_expiry=_fallback_int("ACCESS_TOKEN_EXPIRY", 3600),
        refresh_token_secret=_require("REFRESH_TOKEN_SECRET"),
        refresh_token_expiry=_fallback_int("REFRESH_TOKEN_EXPIRY", 604800),
        seeder_admin_name=_require("SEEDER_ADMIN_NAME"),
        seeder_admin_username=_require("SEEDER_ADMIN_USERNAME"),
        seeder_admin_password=_require("SEEDER_ADMIN_PASSWORD"),
        seeder_user_name=_require("SEEDER_USER_NAME"),
        seeder_user_username=_require("SEEDER_USER_USERNAME"),
        seeder_user_password=_require("SEEDER_USER_PASSWORD"),
        ranging_scheduler_listen_timeout_uus=_fallback_int(
            "RANGING_SCHEDULER_LISTEN_TIMEOUT_UUS",
            120000,
        ),
        ranging_scheduler_initiate_timeout_uus=_fallback_int(
            "RANGING_SCHEDULER_INITIATE_TIMEOUT_UUS",
            12000,
        ),
        ranging_scheduler_listen_to_initiate_delay_ms=_fallback_int(
            "RANGING_SCHEDULER_LISTEN_TO_INITIATE_DELAY_MS",
            80,
        ),
        ranging_scheduler_pair_delay_ms=_fallback_int(
            "RANGING_SCHEDULER_PAIR_DELAY_MS",
            80,
        ),
        ranging_scheduler_idle_delay_ms=_fallback_int(
            "RANGING_SCHEDULER_IDLE_DELAY_MS",
            250,
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
        raise ValidatorDomainException(
            f"Environment variable '{key}' must be an integer."
        ) from e
