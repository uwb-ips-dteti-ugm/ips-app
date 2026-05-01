import json
from datetime import datetime
from ips_app.ports.driven.logging.generic import GenericLoggingPort
from ips_app.domain.models.logging import LogLevel

class JSONGenericLoggingAdapter(GenericLoggingPort):
    def __init__(self, level: LogLevel) -> None:
        self.level = level
        
    def error(self, tag: str, message: str, meta: dict) -> None:
        if self.level >= LogLevel.ERROR:
            self._log(LogLevel.ERROR, tag, message, meta)

    def warn(self, tag: str, message: str, meta: dict) -> None:
        if self.level >= LogLevel.WARN:
            self._log(LogLevel.WARN, tag, message, meta)

    def info(self, tag: str, message: str, meta: dict) -> None:
        if self.level >= LogLevel.INFO:
            self._log(LogLevel.INFO, tag, message, meta)

    def debug(self, tag: str, message: str, meta: dict) -> None:
        if self.level >= LogLevel.DEBUG:
            self._log(LogLevel.DEBUG, tag, message, meta)
    
    def _log(self, level: LogLevel, tag: str, message: str, meta: dict) -> None:
        now = datetime.now()
        timestamp = now.strftime("%d-%m-%Y %H:%M:%S") + f".{now.microsecond // 1000:03d}"
        log_entry = {
            "timestamp": timestamp,
            "level": level.label.upper(),
            "tag": tag,
            "message": message,
            "meta": meta if meta is not None else {}
        }
        print(json.dumps(log_entry))
