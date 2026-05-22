from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, cast

from beanie import Link, PydanticObjectId
from pymongo.errors import DuplicateKeyError

from ips_app.adapters.repository.node.beanie_model import NodeDocument
from ips_app.adapters.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.node import NodeRepository
from ips_app.utils.validator import validate_node_network_assignment


NODE_NETWORK_ID_FIELD = "network._id"


class BeanieNodeRepository(NodeRepository):
    def __init__(self, log: LeveledLogging):
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        created_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> Node:
        tag = f"{self.tag_class}.create_node"
        session = kwargs.get("session")
        try:
            validate_node_network_assignment(network_id, address)
            network = None
            if network_id is not None:
                network = await self._read_node_network_document(network_id, session)
                await self._ensure_network_address_is_available(
                    network_id=network.id,
                    address=cast(int, address),
                    session=session,
                )

            doc = NodeDocument(
                device_id=device_id,
                name=name,
                description=description,
                network=cast(Optional[Link[NodeNetworkDocument]], network),
                address=address,
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
            doc = await self._read_node_document(id, session, fetch_links=True)
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
            doc = await NodeDocument.find_one(
                {"device_id": device_id},
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(device_id, "nodes")
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

    async def read_node_by_network_id_and_address(
        self,
        network_id: Any,
        address: int,
        **kwargs: Any,
    ) -> Node:
        tag = f"{self.tag_class}.read_node_by_network_id_and_address"
        session = kwargs.get("session")
        try:
            network_obj_id = self._to_obj_id(network_id)
            doc = await NodeDocument.find_one(
                {
                    NODE_NETWORK_ID_FIELD: network_obj_id,
                    "address": address,
                },
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(
                    f"{network_id}:{address}",
                    "nodes",
                )
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read node by network and address",
                {
                    "error": str(e),
                    "network_id": str(network_id),
                    "address": address,
                },
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_nodes_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        is_online: Optional[bool] = None,
        **kwargs: Any,
    ) -> Tuple[List[Node], int]:
        tag = f"{self.tag_class}.read_nodes_by_pagination"
        session = kwargs.get("session")
        try:
            query_filter: Dict[str, Any] = {}
            and_filters: List[Dict[str, Any]] = []
            if cursor_id:
                query_filter["_id"] = {"$gt": self._to_obj_id(cursor_id)}
            if search:
                and_filters.append(
                    {
                        "$or": [
                            {"name": {"$regex": search, "$options": "i"}},
                            {"device_id": {"$regex": search, "$options": "i"}},
                            {"description": {"$regex": search, "$options": "i"}},
                        ]
                    }
                )
            if status:
                query_filter["status"] = status.value
            if network_id:
                query_filter[NODE_NETWORK_ID_FIELD] = self._to_obj_id(network_id)
            if address is not None:
                query_filter["address"] = address
            if is_online is not None:
                and_filters.append(self._build_node_online_filter(is_online))
            if and_filters:
                query_filter["$and"] = and_filters

            query = NodeDocument.find(
                query_filter,
                fetch_links=True,
                session=session,
            )
            total = await query.count()
            query = query.sort("_id")
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read nodes by pagination",
                {
                    "error": str(e),
                    "page": page,
                    "limit": limit,
                    "status": str(status) if status else None,
                    "is_online": is_online,
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

    async def update_node_network_assignment_by_id(
        self,
        id: Any,
        network_id: Optional[Any],
        address: Optional[int],
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_network_assignment_by_id"
        session = kwargs.get("session")
        try:
            validate_node_network_assignment(network_id, address)
            doc = await self._read_node_document(id, session)
            network = None
            if network_id is not None:
                network = await self._read_node_network_document(network_id, session)
                await self._ensure_network_address_is_available(
                    network_id=network.id,
                    address=cast(int, address),
                    session=session,
                    excluded_node_id=doc.id,
                )

            await doc.set(
                {
                    "network": network,
                    "address": address,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
                },
                session=session,
            )
        except DuplicateKeyError as e:
            await self.log.error(
                tag,
                "Duplicate node network address on update",
                {"error": str(e), "id": str(id), "network_id": str(network_id)},
            )
            raise DuplicateDomainException("network address", "nodes")
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node network assignment",
                {"error": str(e), "id": str(id), "network_id": str(network_id)},
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
            if status == NodeStatus.APPROVED and (
                doc.network is None or doc.address is None
            ):
                raise ValidatorDomainException(
                    "A node must have a network and address before approval."
                )

            now = datetime.now(timezone.utc)
            update_data: Dict[str, Any] = {
                "status": status,
                "updated_at": now,
                "updated_by": updated_by,
            }
            if status == NodeStatus.APPROVED:
                update_data["approved_at"] = now
                update_data["approved_by"] = updated_by

            await doc.set(update_data, session=session)
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
            await doc.set(
                {
                    "preferences": preferences,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
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

    def _duplicate_field(self, error: DuplicateKeyError) -> str:
        key_pattern = getattr(error, "details", {}) or {}
        key_pattern = key_pattern.get("keyPattern", {})
        if "device_id" in key_pattern:
            return "device_id"
        if "network.$id" in key_pattern and "address" in key_pattern:
            return "network address"
        return "node"

    async def _read_node_document(
        self,
        id: Any,
        session: Any,
        fetch_links: bool = False,
    ) -> NodeDocument:
        doc = await NodeDocument.get(
            self._to_obj_id(id),
            fetch_links=fetch_links,
            session=session,
        )
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

    async def _read_node_network_document(
        self,
        id: Any,
        session: Any,
    ) -> NodeNetworkDocument:
        doc = await NodeNetworkDocument.get(
            self._to_obj_id(id),
            session=session,
        )
        if not doc:
            raise NotFoundDomainException(str(id), "node networks")
        return doc

    async def _ensure_network_address_is_available(
        self,
        network_id: Any,
        address: int,
        session: Any,
        excluded_node_id: Optional[Any] = None,
    ) -> None:
        query_filter: Dict[str, Any] = {
            NODE_NETWORK_ID_FIELD: self._to_obj_id(network_id),
            "address": address,
        }
        if excluded_node_id is not None:
            query_filter["_id"] = {"$ne": self._to_obj_id(excluded_node_id)}

        existing = await NodeDocument.find_one(query_filter, session=session)
        if existing:
            raise DuplicateDomainException("network address", "nodes")

    def _build_node_online_filter(self, is_online: bool) -> Dict[str, Any]:
        if is_online:
            return {
                "$and": [
                    {"last_connected_at": {"$ne": None}},
                    {
                        "$or": [
                            {"last_disconnected_at": None},
                            {
                                "$expr": {
                                    "$gt": [
                                        "$last_connected_at",
                                        "$last_disconnected_at",
                                    ]
                                }
                            },
                        ]
                    },
                ]
            }

        return {
            "$or": [
                {"last_connected_at": None},
                {
                    "$and": [
                        {"last_disconnected_at": {"$ne": None}},
                        {
                            "$expr": {
                                "$lte": [
                                    "$last_connected_at",
                                    "$last_disconnected_at",
                                ]
                            }
                        },
                    ]
                },
            ]
        }

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
