from typing import Union

from fastapi import status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.common import ErrorResponse
from ips_app.controllers.http.dto.record import (
    LatestMultilaterationRecordRequest,
    LatestRangingRecordRequest,
    LatestRecordResponse,
    MultilaterationRecordIntervalRequest,
    RecordsResponse,
    RemovedRecordsResponse,
    RemoveMultilaterationRecordsByIntervalRequest,
    RemoveRangingRecordsByIntervalRequest,
    RangingRecordIntervalRequest,
)
from ips_app.domain.models.exception import (
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.ports.driving.http.record import RecordHTTP


class RecordHandler:
    def __init__(self, service: RecordHTTP):
        self.service = service

    async def get_ranging_records_by_interval(
        self,
        request: RangingRecordIntervalRequest,
    ) -> Union[RecordsResponse, JSONResponse]:
        try:
            request.validate_fields()
            records = await self.service.get_ranging_records_by_interval(
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
                        error="Something went wrong while loading ranging records. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading ranging records. Please try again."
                ).model_dump(),
            )

    async def get_latest_ranging_record(
        self,
        request: LatestRangingRecordRequest,
    ) -> Union[LatestRecordResponse, JSONResponse]:
        try:
            request.validate_fields()
            record = await self.service.get_latest_ranging_record(
                source_node_device_ids=request.source_node_device_ids,
                target_node_device_ids=request.target_node_device_ids,
            )
            return LatestRecordResponse.from_domain(record)
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
                        error="Something went wrong while loading the latest ranging record. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the latest ranging record. Please try again."
                ).model_dump(),
            )

    async def delete_ranging_records_by_interval(
        self,
        request: RemoveRangingRecordsByIntervalRequest,
    ) -> Union[RemovedRecordsResponse, JSONResponse]:
        try:
            request.validate_fields()
            deleted_count = await self.service.remove_ranging_records_by_interval(
                start=request.start,
                end=request.end,
                source_node_device_ids=request.source_node_device_ids,
                target_node_device_ids=request.target_node_device_ids,
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
                        error="Something went wrong while deleting ranging records. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while deleting ranging records. Please try again."
                ).model_dump(),
            )

    async def get_multilateration_records_by_interval(
        self,
        request: MultilaterationRecordIntervalRequest,
    ) -> Union[RecordsResponse, JSONResponse]:
        try:
            request.validate_fields()
            records = await self.service.get_multilateration_records_by_interval(
                start=request.start,
                end=request.end,
                ref_node_device_ids=request.ref_node_device_ids,
                node_device_ids=request.node_device_ids,
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
                        error="Something went wrong while loading multilateration records. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading multilateration records. Please try again."
                ).model_dump(),
            )

    async def get_latest_multilateration_record(
        self,
        request: LatestMultilaterationRecordRequest,
    ) -> Union[LatestRecordResponse, JSONResponse]:
        try:
            request.validate_fields()
            record = await self.service.get_latest_multilateration_record(
                ref_node_device_ids=request.ref_node_device_ids,
                node_device_ids=request.node_device_ids,
            )
            return LatestRecordResponse.from_domain(record)
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
                        error="Something went wrong while loading the latest multilateration record. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the latest multilateration record. Please try again."
                ).model_dump(),
            )

    async def delete_multilateration_records_by_interval(
        self,
        request: RemoveMultilaterationRecordsByIntervalRequest,
    ) -> Union[RemovedRecordsResponse, JSONResponse]:
        try:
            request.validate_fields()
            deleted_count = (
                await self.service.remove_multilateration_records_by_interval(
                    start=request.start,
                    end=request.end,
                    ref_node_device_ids=request.ref_node_device_ids,
                    node_device_ids=request.node_device_ids,
                )
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
                        error="Something went wrong while deleting multilateration records. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while deleting multilateration records. Please try again."
                ).model_dump(),
            )
