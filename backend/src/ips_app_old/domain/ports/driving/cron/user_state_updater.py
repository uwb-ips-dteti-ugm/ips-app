from abc import ABC, abstractmethod


class UserStateUpdaterCron(ABC):
    @abstractmethod
    async def update_user_states(self) -> None:
        """Update user states from last-activity duration cutoffs."""
        ...
