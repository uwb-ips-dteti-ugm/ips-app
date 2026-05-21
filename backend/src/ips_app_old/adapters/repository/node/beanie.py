from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from ips_app_old.adapters.repository.node.beanie_model import NodeDocument
from ips_app_old.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app_old.domain.models.node import Node, NodeStatus
from ips_app_old.domain.ports.driven.logging.generic import GenericLogging
from ips_app_old.domain.ports.driven.repository.node import NodeRepository
from ips_app_old.utils.validator import (
    validate_optional_uwb_network_address,
    validate_uwb_network_value,
)


class BeanieNodeRepository(NodeRepository):
    def __init__(self, log: GenericLogging):
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
        pan_id: Optional[int] = None,
        network_address: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        created_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> Node:
        tag = f"{self.tag_class}.create_node"
        session = kwargs.get("session")
        try:
            validate_optional_uwb_network_address(pan_id, network_address)
            doc = NodeDocument(
                device_id=device_id,
                pan_id=pan_id,
                network_address=network_address,
                name=name,
                description=description,
                preferences=preferences or {},
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            field = self._duplicate_field(e)
            await self.log.error(
                tag,
                "Duplicate node identity",
                {"error": str(e), "field": field, "device_id": device_id},
            )
            raise DuplicateDomainException(field, "nodes")
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create node",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_by_id(self, id: Any, **kwargs: Any) -> Node:
        tag = f"{self.tag_class}.read_node_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_document(id, session)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read node by id",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_by_device_id(
        self,
        device_id: str,
        **kwargs: Any,
    ) -> Node:
        tag = f"{self.tag_class}.read_node_by_device_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_document_by_device_id(device_id, session)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read node by device id",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_by_pan_id(
        self,
        pan_id: int,
        **kwargs: Any,
    ) -> Node:
        tag = f"{self.tag_class}.read_node_by_pan_id"
        session = kwargs.get("session")
        try:
            validate_uwb_network_value(pan_id, "pan_id")
            doc = await NodeDocument.find_one(
                {"pan_id": pan_id},
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(str(pan_id), "nodes")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read node by PAN ID",
                {"error": str(e), "pan_id": pan_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_nodes_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_address: Optional[int] = None,
        **kwargs: Any,
    ) -> Tuple[List[Node], int]:
        tag = f"{self.tag_class}.read_nodes_by_pagination"
        session = kwargs.get("session")
        try:
            query_filter: Dict[str, Any] = {}
            if cursor_id:
                query_filter["_id"] = {"$gt": self._to_obj_id(cursor_id)}
            if search:
                query_filter["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"device_id": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]
            if status:
                query_filter["status"] = status
            if network_address is not None:
                validate_uwb_network_value(network_address, "network_address")
                query_filter["network_address"] = network_address

            query = NodeDocument.find(query_filter, session=session)
            total = await query.count()
            query = query.sort("_id")
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read nodes by pagination",
                {
                    "error": str(e),
                    "page": page,
                    "limit": limit,
                    "network_address": network_address,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_info_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_info_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_document(id, session)
            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
                "version": doc.version + 1,
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description

            await doc.set(update_data, session=session)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node info",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_status_by_id(
        self,
        id: Any,
        status: NodeStatus,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_status_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_document(id, session)
            now = datetime.now(timezone.utc)
            update_data: Dict[str, Any] = {
                "status": status,
                "updated_at": now,
                "updated_by": updated_by,
                "version": doc.version + 1,
            }
            if status == NodeStatus.APPROVED:
                update_data["approved_at"] = now
                update_data["approved_by"] = updated_by

            await doc.set(
                update_data,
                session=session,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node status",
                {"error": str(e), "id": str(id), "status": str(status)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_preferences_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_document(id, session)
            now = datetime.now(timezone.utc)
            await doc.set(
                {
                    "preferences": preferences,
                    "updated_at": now,
                    "updated_by": updated_by,
                    "version": doc.version + 1,
                },
                session=session,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node preferences",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_last_seen_at_by_device_id(
        self,
        device_id: str,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_last_seen_at_by_device_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_document_by_device_id(device_id, session)
            await self._set_node_timestamps(
                doc=doc,
                session=session,
                last_seen_at=datetime.now(timezone.utc),
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node last seen",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_last_connected_at_by_device_id(
        self,
        device_id: str,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_last_connected_at_by_device_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_document_by_device_id(device_id, session)
            now = datetime.now(timezone.utc)
            await self._set_node_timestamps(
                doc=doc,
                session=session,
                last_seen_at=now,
                last_connected_at=now,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node last connected",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_last_disconnected_at_by_device_id(
        self,
        device_id: str,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_last_disconnected_at_by_device_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_document_by_device_id(device_id, session)
            now = datetime.now(timezone.utc)
            await self._set_node_timestamps(
                doc=doc,
                session=session,
                last_seen_at=now,
                last_disconnected_at=now,
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node last disconnected",
                {"error": str(e), "device_id": device_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_node_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_node_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_document(id, session)
            await doc.delete(session=session)
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete node",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    def _to_obj_id(self, value: Any) -> Any:
        if isinstance(value, str) and PydanticObjectId.is_valid(value):
            return PydanticObjectId(value)
        return value

    async def _read_node_document(
        self,
        id: Any,
        session: Any,
    ) -> NodeDocument:
        doc = await NodeDocument.get(self._to_obj_id(id), session=session)
        if not doc:
            raise NotFoundDomainException(str(id), "nodes")
        return doc

    async def _read_node_document_by_device_id(
        self,
        device_id: str,
        session: Any,
    ) -> NodeDocument:
        doc = await NodeDocument.find_one(
            {"device_id": device_id},
            session=session,
        )
        if not doc:
            raise NotFoundDomainException(device_id, "nodes")
        return doc

    async def _set_node_timestamps(
        self,
        doc: NodeDocument,
        session: Any,
        last_seen_at: Optional[datetime] = None,
        last_connected_at: Optional[datetime] = None,
        last_disconnected_at: Optional[datetime] = None,
    ) -> None:
        update_data: Dict[str, Any] = {
            "updated_at": datetime.now(timezone.utc),
        }
        if last_seen_at is not None:
            update_data["last_seen_at"] = last_seen_at
        if last_connected_at is not None:
            update_data["last_connected_at"] = last_connected_at
        if last_disconnected_at is not None:
            update_data["last_disconnected_at"] = last_disconnected_at

        await doc.set(update_data, session=session)

    def _duplicate_field(self, error: DuplicateKeyError) -> str:
        key_pattern = getattr(error, "details", {}) or {}
        key_pattern = key_pattern.get("keyPattern", {})
        if "device_id" in key_pattern:
            return "device_id"
        if "pan_id" in key_pattern and "network_address" in key_pattern:
            return "network_address"
        return "node"
