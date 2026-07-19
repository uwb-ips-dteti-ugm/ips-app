from abc import ABC, abstractmethod

from ips_app.domain.models.user import User


class UserSeeder(ABC):
    @abstractmethod
    async def user_exists(self, username: str) -> bool:
        """Check whether a user with this password username already exists."""
        ...

    @abstractmethod
    async def add_user(
        self,
        name: str,
        username: str,
        password: str,
        role_name: str,
    ) -> User:
        """Add a seeded user with password auth and a role."""
        ...
