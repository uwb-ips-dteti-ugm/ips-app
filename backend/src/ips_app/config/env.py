import os

from ips_app.domain.models.logger import LoggerFormat, LoggerLevel


APP_LOGGER_FORMAT=LoggerFormat.JSON
APP_LOGGER_LEVEL=LoggerLevel.INFO

APP_MONGO_URI="mongodb://USER:PASS@mongo:27017/?authSource=admin&replicaSet=rs0"
APP_MONGO_DB="ips-app"

APP_ACCESS_TOKEN_SECRET="CHANGE_ME"
APP_ACCESS_TOKEN_EXPIRY="1m"
APP_REFRESH_TOKEN_SECRET="CHANGE_ME"
APP_REFRESH_TOKEN_EXPIRY="7d"

APP_SEEDER_ADMIN_NAME="Admin"
APP_SEEDER_ADMIN_USERNAME="admin"
APP_SEEDER_ADMIN_PASSWORD="CHANGE_ME"
APP_SEEDER_USER_NAME="User"
APP_SEEDER_USER_USERNAME="user"
APP_SEEDER_USER_PASSWORD="CHANGE_ME"


def load_env():
    global APP_LOGGER_FORMAT
    global APP_LOGGER_LEVEL
    global APP_MONGO_URI
    global APP_MONGO_DB
    global APP_ACCESS_TOKEN_SECRET
    global APP_ACCESS_TOKEN_EXPIRY
    global APP_REFRESH_TOKEN_SECRET
    global APP_REFRESH_TOKEN_EXPIRY
    global APP_SEEDER_ADMIN_NAME
    global APP_SEEDER_ADMIN_USERNAME
    global APP_SEEDER_ADMIN_PASSWORD
    global APP_SEEDER_USER_NAME
    global APP_SEEDER_USER_USERNAME
    global APP_SEEDER_USER_PASSWORD

    APP_LOGGER_FORMAT = get_logger_format("APP_LOGGER_FORMAT", APP_LOGGER_FORMAT)
    APP_LOGGER_LEVEL = get_logger_level("APP_LOGGER_LEVEL", APP_LOGGER_LEVEL)

    APP_MONGO_URI = get_string("APP_MONGO_URI", APP_MONGO_URI)
    APP_MONGO_DB = get_string("APP_MONGO_DB", APP_MONGO_DB)

    APP_ACCESS_TOKEN_SECRET = get_string("APP_ACCESS_TOKEN_SECRET", APP_ACCESS_TOKEN_SECRET)
    APP_ACCESS_TOKEN_EXPIRY = get_string("APP_ACCESS_TOKEN_EXPIRY", APP_ACCESS_TOKEN_EXPIRY)
    APP_REFRESH_TOKEN_SECRET = get_string("APP_REFRESH_TOKEN_SECRET", APP_REFRESH_TOKEN_SECRET)
    APP_REFRESH_TOKEN_EXPIRY = get_string("APP_REFRESH_TOKEN_EXPIRY", APP_REFRESH_TOKEN_EXPIRY)

    APP_SEEDER_ADMIN_NAME = get_string("APP_SEEDER_ADMIN_NAME", APP_SEEDER_ADMIN_NAME)
    APP_SEEDER_ADMIN_USERNAME = get_string("APP_SEEDER_ADMIN_USERNAME", APP_SEEDER_ADMIN_USERNAME)
    APP_SEEDER_ADMIN_PASSWORD = get_string("APP_SEEDER_ADMIN_PASSWORD", APP_SEEDER_ADMIN_PASSWORD)
    APP_SEEDER_USER_NAME = get_string("APP_SEEDER_USER_NAME", APP_SEEDER_USER_NAME)
    APP_SEEDER_USER_USERNAME = get_string("APP_SEEDER_USER_USERNAME", APP_SEEDER_USER_USERNAME)
    APP_SEEDER_USER_PASSWORD = get_string("APP_SEEDER_USER_PASSWORD", APP_SEEDER_USER_PASSWORD)


def get_string(key: str, fallback: str) -> str:
    val = os.getenv(key)
    if not val:
        return fallback
    else:
        return val


def get_logger_format(key: str, fallback: LoggerFormat) -> LoggerFormat:
    val = os.getenv(key)
    if not val:
        return fallback
    
    if val == LoggerFormat.PLAIN:
        return LoggerFormat.PLAIN
    elif val == LoggerFormat.JSON:
        return LoggerFormat.JSON
    else:
        return fallback


def get_logger_level(key: str, fallback: LoggerLevel) -> LoggerLevel:
    val = os.getenv(key)
    if not val:
        return fallback
    
    if val == LoggerLevel.ERROR:
        return LoggerLevel.ERROR
    elif val == LoggerLevel.WARN:
        return LoggerLevel.WARN
    elif val == LoggerLevel.INFO:
        return LoggerLevel.INFO
    elif val == LoggerLevel.DEBUG:
        return LoggerLevel.DEBUG
    else:
        return fallback