from datetime import datetime
from typing import List, Optional

from ips_app.domain.usecases.ranging import RangingUsecase
from ips_app.presentation.http.dto.ranging import (
    DeleteRangingRecordsResponse,
    RangingRecordResponse,
    ReportRangingMeasurementRequest,
)


class RangingHandler:
    def __init__(self, usecase: RangingUsecase) -> None:
        self.usecase = usecase

    async def post_ranging_report(
        self, request: ReportRangingMeasurementRequest
    ) -> RangingRecordResponse:
        record = await self.usecase.report_ranging_measurement(
            reported_by_device_id=request.reported_by_device_id,
            pan_id=request.pan_id,
            source_address=request.source_address,
            destination_address=request.destination_address,
            distance=request.distance,
        )
        return RangingRecordResponse.from_domain(record)

    async def get_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[str],
        node_id: Optional[str],
    ) -> List[RangingRecordResponse]:
        records = await self.usecase.get_ranging_records_by_interval(
            start=start, end=end, network_id=network_id, node_id=node_id
        )
        return [RangingRecordResponse.from_domain(r) for r in records]

    async def get_latest_ranging_record(
        self, network_id: Optional[str], node_id: Optional[str]
    ) -> Optional[RangingRecordResponse]:
        record = await self.usecase.get_latest_ranging_record(
            network_id=network_id, node_id=node_id
        )
        return RangingRecordResponse.from_domain(record) if record else None

    async def delete_ranging_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[str],
        node_id: Optional[str],
    ) -> DeleteRangingRecordsResponse:
        deleted_count = await self.usecase.delete_ranging_records_by_interval(
            start=start, end=end, network_id=network_id, node_id=node_id
        )
        return DeleteRangingRecordsResponse(deleted_count=deleted_count)
