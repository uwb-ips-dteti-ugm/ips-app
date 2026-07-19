from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, cast

from beanie import Link
from pymongo.errors import DuplicateKeyError

from ips_app.domain.contracts.repository.node import NodeRepository
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.infrastructure.repository._shared.duplicate import duplicate_key_fields
from ips_app.infrastructure.repository._shared.link import find_one_with_links
from ips_app.infrastructure.repository._shared.object_id import to_object_id
from ips_app.infrastructure.repository._shared.pagination import paginate_with_links
from ips_app.infrastructure.repository.node.beanie_model import NodeDocument
from ips_app.infrastructure.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)

NODE_NETWORK_ID_FIELD = "network.$id"


class BeanieNodeRepository(NodeRepository):
    async def create_node(
        self,
        device_id: str,
        name: str,
        description: str = "",
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            self._ensure_network_assignment_is_valid(network_id, address)
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
            raise DuplicateDomainException(self._duplicate_message(e, device_id, address)) from e
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_by_id(self, id: Any, session: Optional[Any] = None) -> Node:
        try:
            doc = await self._read_node_document(id, session, fetch_links=True)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_by_device_id(
        self,
        device_id: str,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            doc = await NodeDocument.find_one(
                {"device_id": device_id},
                fetch_links=True,
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(f"Node '{device_id}' not found")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_by_network_id_and_address(
        self,
        network_id: Any,
        address: int,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            network_obj_id = to_object_id(network_id)
            doc = await find_one_with_links(
                NodeDocument,
                {
                    NODE_NETWORK_ID_FIELD: network_obj_id,
                    "address": address,
                },
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(
                    f"Node with network '{network_id}' and address {address} not found"
                )
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_nodes_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        status: Optional[NodeStatus] = None,
        network_id: Optional[Any] = None,
        address: Optional[int] = None,
        is_online: Optional[bool] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[Node], int]:
        try:
            query_filter: Dict[str, Any] = {}
            and_filters: List[Dict[str, Any]] = []
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
                query_filter[NODE_NETWORK_ID_FIELD] = to_object_id(network_id)
            if address is not None:
                query_filter["address"] = address
            if is_online is not None:
                and_filters.append(self._build_node_online_filter(is_online))
            if and_filters:
                query_filter["$and"] = and_filters

            return await paginate_with_links(
                NodeDocument,
                query_filter,
                page,
                limit,
                NodeDocument.to_domain,
                session=session,
            )
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_info_by_id(
        self,
        id: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            doc = await self._read_node_document(id, session, fetch_links=True)
            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
            }
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description

            await doc.set(update_data, session=session)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_network_assignment_by_id(
        self,
        id: Any,
        network_id: Optional[Any],
        address: Optional[int],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            self._ensure_network_assignment_is_valid(network_id, address)
            doc = await self._read_node_document(id, session, fetch_links=True)
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
            doc.network = cast(Optional[Link[NodeNetworkDocument]], network)
            return doc.to_domain()
        except DuplicateKeyError as e:
            raise DuplicateDomainException(
                f"Address {address} is already assigned in this network"
            ) from e
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_status_by_id(
        self,
        id: Any,
        status: NodeStatus,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            doc = await self._read_node_document(id, session, fetch_links=True)
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
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_preferences_by_id(
        self,
        id: Any,
        preferences: Dict[str, Any],
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            doc = await self._read_node_document(id, session, fetch_links=True)
            await doc.set(
                {
                    "preferences": preferences,
                    "updated_at": datetime.now(timezone.utc),
                    "updated_by": updated_by,
                },
                session=session,
            )
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_last_seen_at_by_device_id(
        self,
        device_id: str,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            doc = await self._read_node_document_by_device_id(
                device_id, session, fetch_links=True
            )
            await self._set_node_timestamps(
                doc=doc,
                session=session,
                last_seen_at=datetime.now(timezone.utc),
            )
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_last_connected_at_by_device_id(
        self,
        device_id: str,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            doc = await self._read_node_document_by_device_id(
                device_id, session, fetch_links=True
            )
            now = datetime.now(timezone.utc)
            await self._set_node_timestamps(
                doc=doc,
                session=session,
                last_seen_at=now,
                last_connected_at=now,
            )
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_last_disconnected_at_by_device_id(
        self,
        device_id: str,
        session: Optional[Any] = None,
    ) -> Node:
        try:
            doc = await self._read_node_document_by_device_id(
                device_id, session, fetch_links=True
            )
            now = datetime.now(timezone.utc)
            await self._set_node_timestamps(
                doc=doc,
                session=session,
                last_seen_at=now,
                last_disconnected_at=now,
            )
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def delete_node_by_id(self, id: Any, session: Optional[Any] = None) -> None:
        try:
            doc = await self._read_node_document(id, session)
            await doc.delete(session=session)
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    def _ensure_network_assignment_is_valid(
        self,
        network_id: Optional[Any],
        address: Optional[int],
    ) -> None:
        if (network_id is None) != (address is None):
            raise ValidatorDomainException(
                "'network_id' and 'address' must be provided together."
            )

    def _duplicate_message(
        self,
        error: DuplicateKeyError,
        device_id: str,
        address: Optional[int],
    ) -> str:
        fields = duplicate_key_fields(error)
        if "device_id" in fields:
            return f"Device ID '{device_id}' already exists"
        if "address" in fields:
            return f"Address {address} is already assigned in this network"
        return "Duplicate node data"

    async def _read_node_document(
        self,
        id: Any,
        session: Optional[Any],
        fetch_links: bool = False,
    ) -> NodeDocument:
        doc = await NodeDocument.get(
            to_object_id(id),
            fetch_links=fetch_links,
            session=session,
        )
        if not doc:
            raise NotFoundDomainException(f"Node '{id}' not found")
        return doc

    async def _read_node_document_by_device_id(
        self,
        device_id: str,
        session: Optional[Any],
        fetch_links: bool = False,
    ) -> NodeDocument:
        doc = await NodeDocument.find_one(
            {"device_id": device_id},
            fetch_links=fetch_links,
            session=session,
        )
        if not doc:
            raise NotFoundDomainException(f"Node '{device_id}' not found")
        return doc

    async def _read_node_network_document(
        self,
        id: Any,
        session: Optional[Any],
    ) -> NodeNetworkDocument:
        doc = await NodeNetworkDocument.get(to_object_id(id), session=session)
        if not doc:
            raise NotFoundDomainException(f"Node network '{id}' not found")
        return doc

    async def _ensure_network_address_is_available(
        self,
        network_id: Any,
        address: int,
        session: Optional[Any],
        excluded_node_id: Optional[Any] = None,
    ) -> None:
        query_filter: Dict[str, Any] = {
            NODE_NETWORK_ID_FIELD: to_object_id(network_id),
            "address": address,
        }
        if excluded_node_id is not None:
            query_filter["_id"] = {"$ne": to_object_id(excluded_node_id)}

        existing = await NodeDocument.find_one(query_filter, session=session)
        if existing:
            raise DuplicateDomainException(
                f"Address {address} is already assigned in this network"
            )

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
        session: Optional[Any],
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
