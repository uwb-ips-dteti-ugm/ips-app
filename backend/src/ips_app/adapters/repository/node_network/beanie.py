from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from ips_app.adapters.repository.node.beanie_model import NodeDocument
from ips_app.adapters.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)
from ips_app.domain.models.exception import (
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.node_network import NodeNetwork
from ips_app.domain.ports.driven.logging.leveled import LeveledLogging
from ips_app.domain.ports.driven.repository.node_network import (
    NodeNetworkRepository,
)


NODE_NETWORK_ID_FIELD = "network._id"


class BeanieNodeNetworkRepository(NodeNetworkRepository):
    def __init__(self, log: LeveledLogging):
        self.log = log
        self.tag_class = self.__class__.__name__

    async def create_node_network(
        self,
        pan_id: int,
        name: str,
        description: str = "",
        created_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> NodeNetwork:
        tag = f"{self.tag_class}.create_node_network"
        session = kwargs.get("session")
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
            await self.log.error(
                tag,
                "Duplicate node network PAN ID",
                {"error": str(e), "pan_id": pan_id},
            )
            raise DuplicateDomainException("pan_id", "node networks")
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to create node network",
                {"error": str(e), "pan_id": pan_id, "name": name},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_network_by_id(
        self,
        id: Any,
        **kwargs: Any,
    ) -> NodeNetwork:
        tag = f"{self.tag_class}.read_node_network_by_id"
        session = kwargs.get("session")
        try:
            doc = await self._read_node_network_document(id, session)
            return doc.to_domain()
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read node network by id",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_network_by_pan_id(
        self,
        pan_id: int,
        **kwargs: Any,
    ) -> NodeNetwork:
        tag = f"{self.tag_class}.read_node_network_by_pan_id"
        session = kwargs.get("session")
        try:
            doc = await NodeNetworkDocument.find_one(
                {"pan_id": pan_id},
                session=session,
            )
            if not doc:
                raise NotFoundDomainException(str(pan_id), "node networks")
            return doc.to_domain()
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read node network by PAN ID",
                {"error": str(e), "pan_id": pan_id},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def read_node_networks_by_pagination(
        self,
        page: int,
        limit: int,
        cursor_id: Optional[Any] = None,
        search: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[List[NodeNetwork], int]:
        tag = f"{self.tag_class}.read_node_networks_by_pagination"
        session = kwargs.get("session")
        try:
            query_filter: Dict[str, Any] = {}
            if cursor_id:
                query_filter["_id"] = {"$gt": self._to_obj_id(cursor_id)}
            if search:
                query_filter["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]
                if search.isdigit():
                    query_filter["$or"].append({"pan_id": int(search)})

            query = NodeNetworkDocument.find(query_filter, session=session)
            total = await query.count()
            query = query.sort("_id")
            docs = await query.skip(page * limit).limit(limit).to_list()
            return [doc.to_domain() for doc in docs], total
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to read node networks by pagination",
                {"error": str(e), "page": page, "limit": limit},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def update_node_network_by_id(
        self,
        id: Any,
        pan_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        tag = f"{self.tag_class}.update_node_network_by_id"
        session = kwargs.get("session")
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
        except DuplicateKeyError as e:
            await self.log.error(
                tag,
                "Duplicate node network PAN ID on update",
                {"error": str(e), "id": str(id), "pan_id": pan_id},
            )
            raise DuplicateDomainException("pan_id", "node networks")
        except NotFoundDomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update node network",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    async def delete_node_network_by_id(self, id: Any, **kwargs: Any) -> None:
        tag = f"{self.tag_class}.delete_node_network_by_id"
        session = kwargs.get("session")
        try:
            network_id = self._to_obj_id(id)
            doc = await self._read_node_network_document(network_id, session)

            node = await NodeDocument.find_one(
                {NODE_NETWORK_ID_FIELD: network_id},
                session=session,
            )
            if node:
                raise ForbiddenDomainException("Node network is used by a node.")

            await doc.delete(session=session)
        except (ForbiddenDomainException, NotFoundDomainException):
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete node network",
                {"error": str(e), "id": str(id)},
            )
            raise UnexpectedDomainException(str(e)) from e

    def _to_obj_id(self, value: Any) -> Any:
        if isinstance(value, str) and PydanticObjectId.is_valid(value):
            return PydanticObjectId(value)
        return value

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
