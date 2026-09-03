from datetime import datetime
from typing import List, Optional

from ips_app.domain.usecases.position import PositionUsecase
from ips_app.presentation.http.dto.position import (
    ComputeTagPositionRequest,
    PositionRecordResponse,
)


class PositionHandler:
    def __init__(self, usecase: PositionUsecase) -> None:
        self.usecase = usecase

    async def post_position_compute(
        self,
        request: ComputeTagPositionRequest,
    ) -> Optional[PositionRecordResponse]:
        record = await self.usecase.compute_and_store_tag_position(
            tag_node_id=request.tag_node_id,
            tag_height=request.tag_height,
        )
        return PositionRecordResponse.from_domain(record) if record else None

    async def get_position_records_by_interval(
        self,
        start: datetime,
        end: datetime,
        network_id: Optional[str],
        tag_node_id: Optional[str],
    ) -> List[PositionRecordResponse]:
        records = await self.usecase.get_position_records_by_interval(
            start, end, network_id, tag_node_id
        )
        return [PositionRecordResponse.from_domain(record) for record in records]

    async def get_latest_position_record(
        self,
        network_id: Optional[str],
        tag_node_id: Optional[str],
    ) -> Optional[PositionRecordResponse]:
        record = await self.usecase.get_latest_position_record(network_id, tag_node_id)
        return PositionRecordResponse.from_domain(record) if record else None
