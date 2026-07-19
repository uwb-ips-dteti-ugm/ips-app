from ips_app.config import env
from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.models.logger import LoggerFormat
from ips_app.infrastructure.logger.leveled.basic import BasicLeveledLogging
from ips_app.infrastructure.logger.leveled.json import JsonLeveledLogging


def create_logger() -> LeveledLogger:
    if env.APP_LOGGER_FORMAT == LoggerFormat.JSON:
        return JsonLeveledLogging(env.APP_LOGGER_LEVEL)
    return BasicLeveledLogging(env.APP_LOGGER_LEVEL)
