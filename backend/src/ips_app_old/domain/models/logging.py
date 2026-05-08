from enum import IntEnum

class LogLevel(IntEnum):
    NONE = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    @property
    def label(self) -> str:
        log_level_str = {
            LogLevel.NONE: "NONE",
            LogLevel.ERROR: "ERROR",
            LogLevel.WARN: "WARN",
            LogLevel.INFO: "INFO",
            LogLevel.DEBUG: "DEBUG"
        }
        return log_level_str[self]