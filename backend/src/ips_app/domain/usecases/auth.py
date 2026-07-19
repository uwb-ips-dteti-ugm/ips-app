from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple


class AuthUsecase(ABC):
    @abstractmethod
    async def sign_in(self, username: str, password: str) -> Tuple[str, str]: ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]: ...

    @abstractmethod
    async def change_password(
        self,
        user_id: Any,
        old_password: str,
        new_password: str,
        updated_by: Optional[Any] = None,
    ) -> None: ...

    @abstractmethod
    async def reset_password(
        self,
        user_id: Any,
        new_password: str,
        updated_by: Optional[Any] = None,
    ) -> None: ...
