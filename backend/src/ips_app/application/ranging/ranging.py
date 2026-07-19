from datetime import datetime
from typing import Any, List, Optional, Sequence

from ips_app.domain.contracts.logger.leveled import LeveledLogger
from ips_app.domain.contracts.repository.node import NodeRepository
from ips_app.domain.contracts.repository.node_network import NodeNetworkRepository
from ips_app.domain.contracts.repository.ranging import RangingRepository
from ips_app.domain.models.exception import (
    DomainException,
    ForbiddenDomainException,
    UnexpectedDomainException,
)
from ips_app.domain.models.node import Node, NodeStatus
from ips_app.domain.models.ranging import RangingRecord
from ips_app.domain.usecases.ranging import RangingUsecase

from ips_app.application._shared.validator import (
    validate_non_empty_string,
    validate_non_negative_float,
    validate_record_interval,
    validate_uwb_value,
)


class BaseRangingUsecase(RangingUsecase):
    def __init__(
        self,
        repo: RangingRepository,
        repo_node: NodeRepository,
        repo_node_network: NodeNetworkRepository,
        log: LeveledLogger,
    ) -> None:
        self.repo = repo
        self.repo_node = repo_node
        self.repo_node_network = repo_node_network
        self.log = log
        self.tag_class = self.__class__.__name__

    async def report_ranging_measurement(
        self,
        reported_by_device_id: str,
        pan_id: int,
        source_address: int,
        destination_address: int,
        distance: float,
    ) -> RangingRecord:
        tag = f"{self.tag_class}/report_ranging_measurement"
        try:
            validate_non_empty_string(reported_by_device_id, "reported_by_device_id")
            validate_uwb_value(pan_id, "pan_id")
            validate_uwb_value(source_address, "source_address")
            validate_uwb_value(destination_address, "destination_address")
            validate_non_negative_float(distance, "distance")

            network = await self.repo_node_network.read_node_network_by_pan_id(pan_id)
            source_node = await self.repo_node.read_node_by_network_id_and_address(
                network_id=network.id, address=source_address
            )
            destination_node = await self.repo_node.read_node_by_network_id_and_address(
                network_id=network.id, address=destination_address
            )

            if source_node.device_id != reported_by_device_id:
                raise ForbiddenDomainException(
                    "Node ranging source must match the reporting device ID."
                )
            self._ensure_approved((source_node, destination_node))

            record = await self.repo.create_ranging_record(
                listener_node_id=source_node.id,
                initiator_node_id=destination_node.id,
                distance=distance,
            )

            for device_id in {source_node.device_id, destination_node.device_id}:
                await self.repo_node.update_node_last_seen_at_by_device_id(device_id)

            await self.log.debug(
                tag,
                "Successfully reported ranging measurement",
                {
                    "reported_by_device_id": reported_by_device_id,
                    "pan_id": pan_id,
                    "source_address": source_address,
                    "destination_address": destination_address,
                    "distance": distance,
                },
            )
            return record
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to report ranging measurement",
                {"error": str(e), "reported_by_device_id": reported_by_device_id},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
    ) -> List[RangingRecord]:
        tag = f"{self.tag_class}/get_ranging_records_by_interval"
        try:
            validate_record_interval(start, end)
            records = await self.repo.read_ranging_records_by_interval(
                start=start,
                end=end,
                network_id=network_id,
                node_id=node_id,
            )
            await self.log.info(
                tag,
                "Successfully retrieved ranging records by interval",
                {"start": start.isoformat(), "end": end.isoformat(), "count": len(records)},
            )
            return records
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to retrieve ranging records by interval",
                {"error": str(e), "start": start.isoformat(), "end": end.isoformat()},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def get_latest_ranging_record(
        self,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
    ) -> Optional[RangingRecord]:
        tag = f"{self.tag_class}/get_latest_ranging_record"
        try:
            record = await self.repo.read_latest_ranging_record(
                network_id=network_id,
                node_id=node_id,
            )
            await self.log.info(
                tag,
                "Successfully retrieved latest ranging record",
                {"found": record is not None},
            )
            return record
        except Exception as e:
            await self.log.error(
                tag, "Failed to retrieve latest ranging record", {"error": str(e)}
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    async def delete_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[Any] = None,
        node_id: Optional[Any] = None,
    ) -> int:
        tag = f"{self.tag_class}/delete_ranging_records_by_interval"
        try:
            validate_record_interval(start, end)
            deleted_count = await self.repo.delete_ranging_records_by_interval(
                start=start,
                end=end,
                network_id=network_id,
                node_id=node_id,
            )
            await self.log.info(
                tag,
                "Successfully deleted ranging records by interval",
                {"start": start.isoformat(), "end": end.isoformat(), "deleted_count": deleted_count},
            )
            return deleted_count
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to delete ranging records by interval",
                {"error": str(e), "start": start.isoformat(), "end": end.isoformat()},
            )
            if isinstance(e, DomainException):
                raise
            raise UnexpectedDomainException(str(e)) from e

    def _ensure_approved(self, nodes: Sequence[Node]) -> None:
        for node in nodes:
            if node.status != NodeStatus.APPROVED:
                raise ForbiddenDomainException("Node is not approved.")
