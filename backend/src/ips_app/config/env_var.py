import os
from dataclasses import dataclass
from dotenv import load_dotenv
from ips_app.domain.models.exception import EnvRequiredException

@dataclass
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

def load_env_var() -> EnvVar:
    def require(key: str) -> str:
        val = os.getenv(key)
        if not val:
            raise EnvRequiredException(key)
        return val

    def fallback(key: str, value: str) -> str:
        val = os.getenv(key, value)
        return val

    load_dotenv()

    return EnvVar(
        log_level=fallback("LOG_LEVEL", "INFO").upper(),
        log_style=fallback("LOG_FORMAT", "basic").lower(),
        mongo_uri=require("MONGO_URI"),
        mongo_db=require("MONGO_DB"),
        access_token_secret=require("ACCESS_TOKEN_SECRET"),
        access_token_expiry=int(fallback("ACCESS_TOKEN_EXPIRY", "3600")),
        refresh_token_secret=require("REFRESH_TOKEN_SECRET"),
        refresh_token_expiry=int(fallback("REFRESH_TOKEN_EXPIRY", "604800")),
        admin_name=fallback("ADMIN_NAME", "admin"),
        admin_username=require("ADMIN_USERNAME"),
        admin_password=require("ADMIN_PASSWORD"),
    )
