from abc import ABC, abstractmethod

class GenericLoggingPort(ABC):
    @abstractmethod
    def error(self, tag: str, message: str, meta: dict) -> None: ...

    @abstractmethod
    def warn(self, tag: str, message: str, meta: dict) -> None: ...

    @abstractmethod
    def info(self, tag: str, message: str, meta: dict) -> None: ...

    @abstractmethod
    def debug(self, tag: str, message: str, meta: dict) -> None: ...