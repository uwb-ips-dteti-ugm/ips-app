from typing import Optional, List, Tuple, Any, Dict
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone
from beanie import PydanticObjectId
from ips_app_old.domain.models.node import Node
from ips_app_old.ports.driven.repository.node import NodeRepositoryPort
from ips_app_old.ports.driven.logging.generic import GenericLoggingPort
from ips_app_old.domain.models.exception import NotFoundException, DuplicateException
from ips_app_old.adapters.driven.repository.node.beanie_model import NodeDocument


class BeanieNodeRepository(NodeRepositoryPort):
    def __init__(self, log: GenericLoggingPort):
        self.log = log
        self.tag_class = "BeanieNodeRepository"

    def _to_obj_id(self, id_val: Any) -> Any:
        if isinstance(id_val, str) and PydanticObjectId.is_valid(id_val):
            return PydanticObjectId(id_val)
        return id_val

    async def create_node(
        self,
        dev_id: str,
        type: str,
        name: str = "Unknown Node",
        description: str = "",
        preferences: Optional[Dict[str, Any]] = None,
        connected: bool = False,
        created_by: Optional[int] = None,
        **kwargs: Any,
    ) -> Node:
        tag = f"{self.tag_class}.create_node"
        session = kwargs.get("session")
        try:
            doc = NodeDocument(
                dev_id=dev_id,
                type=type,
                name=name,
                description=description,
                preferences=preferences or {},
                connected=connected,
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            await self.log.error(tag, "Duplicate node dev_id", {"error": str(e), "dev_id": dev_id})
            raise DuplicateException("dev_id", "nodes")
        except Exception as e:
            await self.log.error(tag, "Failed to create node", {"error": str(e), "dev_id": dev_id})
            raise e

    async def read_node_by_id(self, id: Any, **kwargs: Any) -> Optional[Node]:
        tag = f"{self.tag_class}.read_node_by_id"
        session = kwargs.get("session")
        try:
            doc = await NodeDocument.get(self._to_obj_id(id), session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read node by id", {"error": str(e), "id": str(id)})
            raise e

    async def read_node_by_dev_id(self, dev_id: str, **kwargs: Any) -> Optional[Node]:
        tag = f"{self.tag_class}.read_node_by_dev_id"
        session = kwargs.get("session")
        try:
            doc = await NodeDocument.find_one({"dev_id": dev_id}, session=session)
            return doc.to_domain() if doc else None
        except Exception as e:
            await self.log.error(tag, "Failed to read node by dev_id", {"error": str(e), "dev_id": dev_id})
            raise e

    async def read_nodes_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        type: Optional[str] = None,
        connected: Optional[bool] = None,
        approved: Optional[bool] = None,
        **kwargs: Any,
    ) -> Tuple[List[Node], int]:
        tag = f"{self.tag_class}.read_nodes_by_pagination"
        session = kwargs.get("session")
        try:
            query_filter: Dict[str, Any] = {}
            if search:
                query_filter["$or"] = [
                    {"dev_id": {"$regex": search, "$options": "i"}},
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]
            if type:
                query_filter["type"] = type
            if connected is not None:
                query_filter["connected"] = connected
            if approved is not None:
                query_filter["approved_at"] = {"$ne": None} if approved else None
            if cursor_id:
                query_filter["_id"] = {"$gt": self._to_obj_id(cursor_id)}

            query = NodeDocument.find(query_filter, session=session)
            total = await query.count()
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(tag, "Failed to read nodes by pagination", {"error": str(e)})
            raise e

    async def update_node_info_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[str] = None,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_info_by_id"
        session = kwargs.get("session")
        try:
            doc = await NodeDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundException(str(id), "nodes")

            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if type is not None:
                update_data["type"] = type

            await doc.set(update_data, session=session)
        except NotFoundException:
            raise
        except Exception as e:
            await self.log.error(tag, "Failed to update node info", {"error": str(e), "id": str(id)})
            raise e

    async def update_node_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_preferences_by_id"
        session = kwargs.get("session")
        try:
            doc = await NodeDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundException(str(id), "nodes")

            await doc.set({
                "preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update node preferences", {"error": str(e), "id": str(id)})
            raise e

    async def update_node_connected_by_id(
        self,
        id: Any,
        connected: bool,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_connected_by_id"
        session = kwargs.get("session")
        try:
            doc = await NodeDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundException(str(id), "nodes")

            await doc.set({
                "connected": connected,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update node connection state", {"error": str(e), "id": str(id)})
            raise e

    async def update_node_connected_by_dev_id(
        self,
        dev_id: str,
        connected: bool,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_connected_by_dev_id"
        session = kwargs.get("session")
        try:
            doc = await NodeDocument.find_one({"dev_id": dev_id}, session=session)
            if not doc:
                raise NotFoundException(dev_id, "nodes")

            await doc.set({
                "connected": connected,
                "updated_at": datetime.now(timezone.utc),
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to update node connection state by dev_id", {"error": str(e), "dev_id": dev_id})
            raise e

    async def approve_node_by_id(
        self,
        id: Any,
        approved_by: Any,
        approved_at: Optional[datetime] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.approve_node_by_id"
        session = kwargs.get("session")
        try:
            doc = await NodeDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundException(str(id), "nodes")

            now = datetime.now(timezone.utc)
            await doc.set({
                "approved_at": approved_at or now,
                "approved_by": approved_by,
                "updated_at": now,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to approve node", {"error": str(e), "id": str(id)})
            raise e

    async def revoke_node_approval_by_id(
        self,
        id: Any,
        updated_by: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.revoke_node_approval_by_id"
        session = kwargs.get("session")
        try:
            doc = await NodeDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundException(str(id), "nodes")

            await doc.set({
                "approved_at": None,
                "approved_by": None,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }, session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to revoke node approval", {"error": str(e), "id": str(id)})
            raise e

    async def delete_node_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_node_by_id"
        session = kwargs.get("session")
        try:
            doc = await NodeDocument.get(self._to_obj_id(id), session=session)
            if not doc:
                raise NotFoundException(str(id), "nodes")
            await doc.delete(session=session)
        except Exception as e:
            await self.log.error(tag, "Failed to delete node", {"error": str(e), "id": str(id)})
            raise e
