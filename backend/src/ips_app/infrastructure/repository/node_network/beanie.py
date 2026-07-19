from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pymongo.errors import DuplicateKeyError

from ips_app.domain.contracts.repository.node_network import NodeNetworkRepository
from ips_app.domain.models.exception import (
    DomainException,
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.node_network import NodeNetwork
from ips_app.infrastructure.repository._shared.object_id import to_object_id
from ips_app.infrastructure.repository._shared.pagination import paginate
from ips_app.infrastructure.repository.node.beanie_model import NodeDocument
from ips_app.infrastructure.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)

NODE_NETWORK_ID_FIELD = "network.$id"


class BeanieNodeNetworkRepository(NodeNetworkRepository):
    async def create_node_network(
        self,
        pan_id: int,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> NodeNetwork:
        try:
            doc = NodeNetworkDocument(
                pan_id=pan_id,
                name=name,
                description=description,
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            raise DuplicateDomainException(f"PAN ID {pan_id} already exists") from e
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_network_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> NodeNetwork:
        try:
            doc = await self._read_node_network_document(id, session)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_network_by_pan_id(
        self,
        pan_id: int,
        session: Optional[Any] = None,
    ) -> NodeNetwork:
        try:
            doc = await NodeNetworkDocument.find_one(
                {"pan_id": pan_id},
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(f"Node network with PAN ID {pan_id} not found")
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_networks_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[NodeNetwork], int]:
        try:
            query_filter: Dict[str, Any] = {}
            if search:
                or_filters: List[Dict[str, Any]] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]
                if search.isdigit():
                    or_filters.append({"pan_id": int(search)})
                query_filter["$or"] = or_filters

            query = NodeNetworkDocument.find(query_filter, session=session)
            return await paginate(query, page, limit, NodeNetworkDocument.to_domain)
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_network_by_id(
        self,
        id: Any,
        pan_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> NodeNetwork:
        try:
            doc = await self._read_node_network_document(id, session)
            update_data: Dict[str, Any] = {
                "updated_at": datetime.now(timezone.utc),
                "updated_by": updated_by,
            }
            if pan_id is not None:
                update_data["pan_id"] = pan_id
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description

            await doc.set(update_data, session=session)
            return doc.to_domain()
        except DuplicateKeyError as e:
            raise DuplicateDomainException(f"PAN ID {pan_id} already exists") from e
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def delete_node_network_by_id(
        self,
        id: Any,
        session: Optional[Any] = None,
    ) -> None:
        try:
            network_id = to_object_id(id)
            doc = await self._read_node_network_document(network_id, session)

            node = await NodeDocument.find_one(
                {NODE_NETWORK_ID_FIELD: network_id},
                session=session,
            )
            if node:
                raise ForbiddenDomainException("Node network is used by a node.")

            await doc.delete(session=session)
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def _read_node_network_document(
        self,
        id: Any,
        session: Optional[Any],
    ) -> NodeNetworkDocument:
        doc = await NodeNetworkDocument.get(to_object_id(id), session=session)
        if not doc:
            raise NotFoundDomainException(f"Node network '{id}' not found")
        return doc
