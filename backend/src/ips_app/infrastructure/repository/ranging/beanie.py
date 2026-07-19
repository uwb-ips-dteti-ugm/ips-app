from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

from beanie import Link
from beanie.operators import In

from ips_app.domain.contracts.repository.ranging import RangingRepository
from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.ranging import RangingRecord
from ips_app.infrastructure.repository._shared.link import link_id, resolved_link
from ips_app.infrastructure.repository._shared.object_id import to_object_id
from ips_app.infrastructure.repository.node.beanie_model import NodeDocument
from ips_app.infrastructure.repository.node_network.beanie_model import (
    NodeNetworkDocument,
)
from ips_app.infrastructure.repository.ranging.beanie_model import (
    RangingRecordDocument,
)


class BeanieRangingRepository(RangingRepository):
    async def create_ranging_record(
        self,
        listener_node_id: Any,
        initiator_node_id: Any,
        distance: float,
        recorded_at: Optional[datetime] = None,
        session: Optional[Any] = None,
    ) -> RangingRecord:
        try:
            listener = await self._read_node_document(listener_node_id, session)
            initiator = await self._read_node_document(initiator_node_id, session)

            listener_network_id = link_id(listener.network)
            initiator_network_id = link_id(initiator.network)
            if listener_network_id is None or initiator_network_id is None:
                raise ValidatorDomainException(
                    "Both nodes must belong to the same network to record a ranging measurement."
                )
            if str(listener_network_id) != str(initiator_network_id):
                raise ValidatorDomainException(
                    "Both nodes must belong to the same network to record a ranging measurement."
                )

            network = resolved_link(listener.network, field_name="network")

            doc = RangingRecordDocument(
                network=cast(Link[NodeNetworkDocument], network),
                listener_node=cast(Link[NodeDocument], listener),
                initiator_node=cast(Link[NodeDocument], initiator),
                distance=distance,
                recorded_at=recorded_at or datetime.now(timezone.utc),
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> List[RangingRecord]:
        try:
            query_filter = self._build_filter(start, end, network_id, node_id)
            docs = await self._find_with_links(
                query_filter, sort="recorded_at", session=session
            )
            return [doc.to_domain() for doc in docs]
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_latest_ranging_record(
        self,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Optional[RangingRecord]:
        try:
            query_filter = self._build_filter(None, None, network_id, node_id)
            docs = await self._find_with_links(
                query_filter, sort="-recorded_at", limit=1, session=session
            )
            if not docs:
                return None
            return docs[0].to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def delete_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> int:
        try:
            query_filter = self._build_filter(start, end, network_id, node_id)
            result = await RangingRecordDocument.get_motor_collection().delete_many(
                query_filter,
                session=session,
            )
            return result.deleted_count
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    def _build_filter(
        self,
        start: Optional[datetime],
        end: Optional[datetime],
        network_id: Optional[Any],
        node_id: Optional[Any],
    ) -> Dict[str, Any]:
        query_filter: Dict[str, Any] = {}
        if start is not None and end is not None:
            if start > end:
                raise ValidatorDomainException("'start' must not be after 'end'.")
            query_filter["recorded_at"] = {"$gte": start, "$lte": end}
        if network_id is not None:
            query_filter["network.$id"] = to_object_id(network_id)
        if node_id is not None:
            node_obj_id = to_object_id(node_id)
            query_filter["$or"] = [
                {"listener_node.$id": node_obj_id},
                {"initiator_node.$id": node_obj_id},
            ]
        return query_filter

    async def _find_with_links(
        self,
        query_filter: Dict[str, Any],
        sort: str,
        session: Optional[Any],
        limit: Optional[int] = None,
    ) -> List[RangingRecordDocument]:
        # Filtering on a Link's nested id (network.$id, listener_node.$id, ...) only
        # matches against the raw, unresolved documents, so the filtered/sorted query
        # must run without fetch_links first; the matching ids are then re-fetched
        # with fetch_links=True (and nesting_depth=2, since Node.network is itself a
        # link) to build fully resolved RangingRecord domain objects.
        query = RangingRecordDocument.find(query_filter, session=session).sort(sort)
        if limit is not None:
            query = query.limit(limit)
        ordered_ids = [doc.id for doc in await query.to_list()]
        if not ordered_ids:
            return []

        resolved_docs = await RangingRecordDocument.find(
            In(RangingRecordDocument.id, ordered_ids),
            fetch_links=True,
            nesting_depth=2,
            session=session,
        ).to_list()
        by_id = {doc.id: doc for doc in resolved_docs}
        return [by_id[doc_id] for doc_id in ordered_ids if doc_id in by_id]

    async def _read_node_document(
        self,
        id: Any,
        session: Optional[Any],
    ) -> NodeDocument:
        doc = await NodeDocument.get(
            to_object_id(id),
            fetch_links=True,
            session=session,
        )
        if not doc:
            raise NotFoundDomainException(f"Node '{id}' not found")
        return doc
