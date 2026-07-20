from abc import ABC, abstractmethod


class NameGenerator(ABC):
    @abstractmethod
    def generate(self) -> str: ...
