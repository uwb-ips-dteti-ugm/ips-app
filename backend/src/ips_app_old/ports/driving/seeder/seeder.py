from abc import ABC, abstractmethod


class SeederPort(ABC):
    @abstractmethod
    async def seed_permissions(self) -> None:
        """Idempotently seed initial permissions."""
        ...

    @abstractmethod
    async def seed_roles(self) -> None:
        """Idempotently seed initial roles and assign permissions."""
        ...

    @abstractmethod
    async def seed_features(self) -> None:
        """Idempotently seed initial features and link permissions."""
        ...

    @abstractmethod
    async def seed_accounts(self) -> None:
        """Idempotently seed initial user accounts."""
        ...
