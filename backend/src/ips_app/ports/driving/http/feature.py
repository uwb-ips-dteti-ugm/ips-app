from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any
from ips_app.domain.models.feature import Feature
from ips_app.domain.models.permission import Permission

class FeatureHTTPPort(ABC):
    @abstractmethod
    async def add_feature(self, name: str, description: str) -> Feature:
        """Add a new feature."""
        ...

    @abstractmethod
    async def get_feature(self, feature_id: Any) -> Feature:
        """Get a feature by its ID."""
        ...

    @abstractmethod
    async def get_features(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None
    ) -> Tuple[List[Feature], int]:
        """Get a list of features with pagination."""
        ...

    @abstractmethod
    async def set_feature(
        self, 
        feature_id: Any, 
        name: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Feature:
        """Update a feature's basic information."""
        ...

    @abstractmethod
    async def set_feature_preferences(self, feature_id: Any, preferences: bytes) -> Feature:
        """Update a feature's preferences."""
        ...

    @abstractmethod
    async def remove_feature(self, feature_id: Any) -> str:
        """Remove a feature."""
        ...

    @abstractmethod
    async def add_permissions_to_feature(self, feature_id: Any, permission_ids: List[Any]) -> Feature:
        """Bind permissions to a feature."""
        ...

    @abstractmethod
    async def remove_permissions_from_feature(self, feature_id: Any, permission_ids: List[Any]) -> Feature:
        """Unbind permissions from a feature."""
        ...

    @abstractmethod
    async def get_feature_permissions(self, feature_id: Any) -> List[Permission]:
        """Get permissions bound to a feature."""
        ...

    @abstractmethod
    async def get_accessible_features(self, user_id: Any) -> List[Feature]:
        """Get all features accessible by a user."""
        ...

    @abstractmethod
    async def can_access_feature(self, user_id: Any, feature_id: Any) -> bool:
        """Check if a user can access a specific feature."""
        ...
