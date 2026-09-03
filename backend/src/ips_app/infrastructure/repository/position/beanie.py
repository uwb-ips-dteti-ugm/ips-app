from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

from beanie import Link
from beanie.operators import In

from ips_app.domain.contracts.repository.position import PositionRepository
from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.position import PositionRecord
from ips_app.infrastructure.repository._shared.object_id import get_by_id, to_object_id
from ips_app.infrastructure.repository.node.beanie_model import NodeDocument
from ips_app.infrastructure.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)
from ips_app.infrastructure.repository.position.beanie_model import (
    PositionRecordDocument,
)


class BeaniePositionRepository(PositionRepository):
    async def create_position_record(
        self,
        network_id: Any,
        tag_node_id: Any,
        x: float,
        y: float,
        tag_height: float,
        computed_at: Optional[datetime] = None,
        session: Optional[Any] = None,
    ) -> PositionRecord:
        try:
            network = await self._read_node_network_document(network_id, session)
            tag_node = await self._read_node_document(tag_node_id, session)

            doc = PositionRecordDocument(
                network=cast(Link[NodeNetworkDocument], network),
                tag_node=cast(Link[NodeDocument], tag_node),
                x=x,
                y=y,
                tag_height=tag_height,
                computed_at=computed_at or datetime.now(timezone.utc),
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_position_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        tag_node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> List[PositionRecord]:
        try:
            query_filter = self._build_filter(start, end, network_id, tag_node_id)
            docs = await self._find_with_links(
                query_filter, sort="computed_at", session=session
            )
            return [doc.to_domain() for doc in docs]
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_latest_position_record(
        self,
        network_id: Optional[Any] = None,
        tag_node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Optional[PositionRecord]:
        try:
            query_filter = self._build_filter(None, None, network_id, tag_node_id)
            docs = await self._find_with_links(
                query_filter, sort="-computed_at", limit=1, session=session
            )
            if not docs:
                return None
            return docs[0].to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    def _build_filter(
        self,
        start: Optional[datetime],
        end: Optional[datetime],
        network_id: Optional[Any],
        tag_node_id: Optional[Any],
    ) -> Dict[str, Any]:
        query_filter: Dict[str, Any] = {}
        if start is not None and end is not None:
            query_filter["computed_at"] = {"$gte": start, "$lte": end}
        if network_id is not None:
            query_filter["network.$id"] = to_object_id(network_id)
        if tag_node_id is not None:
            query_filter["tag_node.$id"] = to_object_id(tag_node_id)
        return query_filter

    async def _find_with_links(
        self,
        query_filter: Dict[str, Any],
        sort: str,
        session: Optional[Any],
        limit: Optional[int] = None,
    ) -> List[PositionRecordDocument]:
        # Same two-step workaround as ranging records: filtering on a Link's nested
        # id only matches the raw, unresolved documents, so the filtered/sorted
        # query has to run before fetch_links -- the matching ids are then
        # re-fetched with fetch_links=True (nesting_depth=2, since tag_node.network
        # is itself a link) to build fully resolved PositionRecord domain objects.
        query = PositionRecordDocument.find(query_filter, session=session).sort(sort)
        if limit is not None:
            query = query.limit(limit)
        ordered_ids = [doc.id for doc in await query.to_list()]
        if not ordered_ids:
            return []

        resolved_docs = await PositionRecordDocument.find(
            In(PositionRecordDocument.id, ordered_ids),
            fetch_links=True,
            nesting_depth=2,
            session=session,
        ).to_list()
        by_id = {
            doc.id: doc
            for doc in resolved_docs
            # A record whose network/tag_node has since been deleted can't be
            # fetch_links-resolved -- excluded here rather than crashing the
            # whole list for one stale record (mirrors ranging's repository).
            if not (isinstance(doc.network, Link) or isinstance(doc.tag_node, Link))
        }
        return [by_id[doc_id] for doc_id in ordered_ids if doc_id in by_id]

    async def _read_node_document(
        self,
        id: Any,
        session: Optional[Any],
    ) -> NodeDocument:
        doc = await get_by_id(NodeDocument, id, fetch_links=True, session=session)
        if not doc:
            raise NotFoundDomainException(f"Node '{id}' not found")
        return doc

    async def _read_node_network_document(
        self,
        id: Any,
        session: Optional[Any],
    ) -> NodeNetworkDocument:
        doc = await get_by_id(NodeNetworkDocument, id, session=session)
        if not doc:
            raise NotFoundDomainException(f"Node network '{id}' not found")
        return doc
