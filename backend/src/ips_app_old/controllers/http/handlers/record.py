from typing import Union

from fastapi.responses import JSONResponse

from ips_app_old.controllers.http.dto.record import (
    RecordIntervalRequest,
    RecordsResponse,
    RemovedRecordsResponse,
    RemoveRecordsByIntervalRequest,
)
from ips_app_old.controllers.http.handlers.exception import handle_exception
from ips_app_old.domain.ports.driving.http.record import RecordHTTP


class RecordHandler:
    def __init__(self, service: RecordHTTP):
        self.service = service

    def _handle_exception(self, error: Exception) -> JSONResponse:
        return handle_exception(error)

    async def get_records_by_interval(
        self,
        request: RecordIntervalRequest,
    ) -> Union[RecordsResponse, JSONResponse]:
        try:
            request.validate_fields()
            records = await self.service.get_records_by_interval(
                label=request.label,
                interval_field=request.interval_field,
                start=request.start,
                end=request.end,
                source_node_device_ids=request.source_node_device_ids,
                target_node_device_ids=request.target_node_device_ids,
            )
            return RecordsResponse.from_domain(records)
        except Exception as e:
            return self._handle_exception(e)

    async def delete_records_by_interval(
        self,
        request: RemoveRecordsByIntervalRequest,
    ) -> Union[RemovedRecordsResponse, JSONResponse]:
        try:
            request.validate_fields()
            deleted_count = await self.service.remove_records_by_interval(
                label=request.label,
                interval_field=request.interval_field,
                start=request.start,
                end=request.end,
                source_node_device_ids=request.source_node_device_ids,
            )
            return RemovedRecordsResponse(deleted_count=deleted_count)
        except Exception as e:
            return self._handle_exception(e)
