import json
from datetime import datetime
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.models.log import LogLevel


class BasicLeveledLogging(LeveledLogging):
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
        level_str = level.label.upper()
        meta_str = json.dumps(meta) if meta else "{}"
        print(f"{timestamp} [{level_str}] [{tag}] {message} | {meta_str}", flush=True)
