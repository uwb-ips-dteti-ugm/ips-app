from typing import Union

from fastapi import status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.controllers.http.dto.record import (
    RecordIntervalRequest,
    RecordsResponse,
    RemovedRecordsResponse,
    RemoveRecordsByIntervalRequest,
)
from ips_app.domain.models.exception import (
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.ports.driving.http.record import RecordHTTP


class RecordHandler:
    def __init__(self, service: RecordHTTP):
        self.service = service

    async def get_records_by_interval(
        self,
        request: RecordIntervalRequest,
    ) -> Union[RecordsResponse, JSONResponse]:
        try:
            request.validate_fields()
            records = await self.service.get_records_by_interval(
                label=request.label,
                start=request.start,
                end=request.end,
                source_node_device_ids=request.source_node_device_ids,
                target_node_device_ids=request.target_node_device_ids,
            )
            return RecordsResponse.from_domain(records)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading records. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading records. Please try again."
                ).model_dump(),
            )

    async def delete_records_by_interval(
        self,
        request: RemoveRecordsByIntervalRequest,
    ) -> Union[RemovedRecordsResponse, JSONResponse]:
        try:
            request.validate_fields()
            deleted_count = await self.service.remove_records_by_interval(
                label=request.label,
                start=request.start,
                end=request.end,
                source_node_device_ids=request.source_node_device_ids,
            )
            return RemovedRecordsResponse(deleted_count=deleted_count)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while deleting records. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while deleting records. Please try again."
                ).model_dump(),
            )
