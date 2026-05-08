import json
from datetime import datetime
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.models.log import LogLevel

class JSONGenericLogging(GenericLogging):
    def __init__(self, level: LogLevel) -> None:
        self.level = level
        
    async def error(self, tag: str, message: str, meta: dict) -> None:
        if self.level >= LogLevel.ERROR:
            await self._log(LogLevel.ERROR, tag, message, meta)

    async def warn(self, tag: str, message: str, meta: dict) -> None:
        if self.level >= LogLevel.WARN:
            await self._log(LogLevel.WARN, tag, message, meta)

    async def info(self, tag: str, message: str, meta: dict) -> None:
        if self.level >= LogLevel.INFO:
            await self._log(LogLevel.INFO, tag, message, meta)

    async def debug(self, tag: str, message: str, meta: dict) -> None:
        if self.level >= LogLevel.DEBUG:
            await self._log(LogLevel.DEBUG, tag, message, meta)
    
    async def _log(self, level: LogLevel, tag: str, message: str, meta: dict) -> None:
        now = datetime.now()
        timestamp = now.strftime("%d-%m-%Y %H:%M:%S") + f".{now.microsecond // 1000:03d}"
        log_entry = {
            "timestamp": timestamp,
            "level": level.label.upper(),
            "tag": tag,
            "message": message,
            "meta": meta if meta is not None else {}
        }
        print(json.dumps(log_entry), flush=True)
