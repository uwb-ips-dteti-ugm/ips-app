from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any, Dict
from ips_app.domain.models.feature import Feature
from ips_app.domain.models.permission import Permission

class FeatureRepositoryPort(ABC):
    @abstractmethod
    async def create_feature(
        self, 
        name: str, 
        description: str, 
        created_by: Optional[int] = None
    ) -> Feature:
        """Create a new feature."""
        ...

    @abstractmethod
    async def read_feature_by_id(self, id: Any) -> Optional[Feature]:
        """Read a feature by its ID."""
        ...

    @abstractmethod
    async def read_features_by_pagination(
        self, 
        page: int, 
        limit: int, 
        cursor_id: Optional[Any] = None, 
        search: Optional[str] = None
    ) -> Tuple[List[Feature], int]:
        """Read features with pagination and search."""
        ...

    @abstractmethod
    async def update_feature_by_id(
        self, 
        id: Any, 
        name: Optional[str] = None, 
        description: Optional[str] = None, 
        updated_by: Optional[int] = None
    ) -> None:
        """Update feature name or description."""
        ...

    @abstractmethod
    async def update_feature_preferences_by_id(
        self, 
        id: Any, 
        preferences: Dict[str, Any], 
        updated_by: Optional[int] = None
    ) -> None:
        """Update feature preferences."""
        ...

    @abstractmethod
    async def delete_feature_by_id(self, id: Any) -> None:
        """Delete a feature by its ID."""
        ...
        
    @abstractmethod
    async def add_permissions_to_feature(self, id: Any, permission_ids: List[Any], updated_by: Optional[int] = None) -> None:
        """Add permissions to a feature."""
        ...
        
    @abstractmethod
    async def remove_permissions_from_feature(self, id: Any, permission_ids: List[Any], updated_by: Optional[int] = None) -> None:
        """Remove permissions from a feature."""
        ...
