from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.repository.node import NodeRepository
from ips_app.domain.contracts.repository.position import PositionRepository
from ips_app.domain.contracts.repository.ranging import RangingRepository
from ips_app.domain.models.exception import (
    DomainException,
    ForbiddenDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.domain.models.position import PositionRecord
from ips_app.domain.models.ranging import RangingRecord
from ips_app.domain.usecases.position import PositionUsecase

from ips_app.application._shared.validator import (
    validate_non_negative_float,
    validate_record_interval,
)
from ips_app.application.position.trilateration import (
    MIN_ANCHORS,
    AnchorReading,
    solve_trilateration_2d,
)

# How far back to look for a "recent enough to still be relevant" distance
# reading between the tag and a given anchor.
LATEST_READING_WINDOW = timedelta(minutes=10)


class BasePositionUsecase(PositionUsecase):
    def __init__(
        self,
        repo: PositionRepository,
        repo_node: NodeRepository,
        repo_ranging: RangingRepository,
        log: LeveledLogger,
    ) -> None:
        self.repo = repo
        self.repo_node = repo_node
        self.repo_ranging = repo_ranging
        self.log = log
        self.tag_class = self.__class__.__name__

    async def compute_and_store_tag_position(
        self,
        tag_node_id: Any,
        tag_height: float,
    ) -> Optional[PositionRecord]:
        tag = f"{self.tag_class}/compute_and_store_tag_position"
        try:
            validate_non_negative_float(tag_height, "tag_height")

            tag_node = await self.repo_node.read_node_by_id(tag_node_id)
            if tag_node.status != NodeStatus.APPROVED:
                raise ForbiddenDomainException("Node is not approved.")
            if tag_node.network is None:
                raise ValidatorDomainException(
                    "Node must be assigned to a network to compute its position."
                )

            anchors = [
                anchor
                for anchor in await self.repo_node.read_anchor_nodes_by_network_id(
                    tag_node.network.id
                )
                if str(anchor.id) != str(tag_node.id)
            ]
            if len(anchors) < MIN_ANCHORS:
                await self.log.info(
                    tag,
                    "Not enough anchors configured in network to compute a position",
                    {"tag_node_id": str(tag_node_id), "anchor_count": len(anchors)},
                )
                return None

            readings = await self._collect_anchor_readings(tag_node, anchors)
            if len(readings) < MIN_ANCHORS:
                await self.log.info(
                    tag,
                    "Not enough recent anchor readings to compute a position",
                    {"tag_node_id": str(tag_node_id), "reading_count": len(readings)},
                )
                return None

            solved = solve_trilateration_2d(readings, tag_height)
            if solved is None:
                await self.log.info(
                    tag,
                    "Trilateration solve did not converge",
                    {"tag_node_id": str(tag_node_id)},
                )
                return None

            record = await self.repo.create_position_record(
                network_id=tag_node.network.id,
                tag_node_id=tag_node.id,
                x=solved.x,
                y=solved.y,
                tag_height=tag_height,
            )
            await self.log.info(
                tag,
                "Successfully computed and stored tag position",
                {"tag_node_id": str(tag_node_id), "x": solved.x, "y": solved.y},
            )
            return record
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to compute tag position",
                {"error": str(e), "tag_node_id": str(tag_node_id)},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_position_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        tag_node_id: Optional[Any] = None,
    ) -> List[PositionRecord]:
        tag = f"{self.tag_class}/get_position_records_by_interval"
        try:
            validate_record_interval(start, end)
            records = await self.repo.read_position_records_by_interval(
                start=start,
                end=end,
                network_id=network_id,
                tag_node_id=tag_node_id,
            )
            await self.log.info(
                tag,
                "Successfully retrieved position records by interval",
                {"start": start.isoformat(), "end": end.isoformat(), "count": len(records)},
            )
            return records
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve position records by interval",
                {"error": str(e), "start": start.isoformat(), "end": end.isoformat()},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_latest_position_record(
        self,
        network_id: Optional[Any] = None,
        tag_node_id: Optional[Any] = None,
    ) -> Optional[PositionRecord]:
        tag = f"{self.tag_class}/get_latest_position_record"
        try:
            record = await self.repo.read_latest_position_record(
                network_id=network_id,
                tag_node_id=tag_node_id,
            )
            await self.log.info(
                tag,
                "Successfully retrieved latest position record",
                {"found": record is not None},
            )
            return record
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve latest position record", {"error": str(e)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def _collect_anchor_readings(
        self,
        tag_node: Node,
        anchors: List[Node],
    ) -> List[AnchorReading]:
        end = datetime.now(timezone.utc)
        start = end - LATEST_READING_WINDOW
        recent_records = await self.repo_ranging.read_ranging_records_by_interval(
            start=start,
            end=end,
            node_id=tag_node.id,
        )

        latest_by_anchor_id = self._pick_latest_record_per_counterpart(
            recent_records, tag_node.id, {str(anchor.id) for anchor in anchors}
        )

        readings: List[AnchorReading] = []
        for anchor in anchors:
            record = latest_by_anchor_id.get(str(anchor.id))
            if record is None or anchor.position is None:
                continue
            readings.append(
                AnchorReading(
                    x=anchor.position.x,
                    y=anchor.position.y,
                    z=anchor.position.z,
                    distance=record.distance,
                )
            )
        return readings

    def _pick_latest_record_per_counterpart(
        self,
        records: List[RangingRecord],
        tag_node_id: Any,
        anchor_ids: set,
    ) -> Dict[str, RangingRecord]:
        latest_by_counterpart_id: Dict[str, RangingRecord] = {}
        for record in records:
            counterpart = (
                record.initiator_node
                if str(record.listener_node.id) == str(tag_node_id)
                else record.listener_node
            )
            counterpart_id = str(counterpart.id)
            if counterpart_id not in anchor_ids:
                continue

            existing = latest_by_counterpart_id.get(counterpart_id)
            if existing is not None and existing.recorded_at >= record.recorded_at:
                continue
            latest_by_counterpart_id[counterpart_id] = record

        return latest_by_counterpart_id
