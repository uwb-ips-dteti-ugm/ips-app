import hashlib
from typing import Any, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from ips_app.domain.contracts.repository.firmware import FirmwareRepository
from ips_app.domain.models.exception import (
    DomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.models.firmware import Firmware
from ips_app.infrastructure.repository._shared.object_id import get_by_id
from ips_app.infrastructure.repository._shared.pagination import paginate
from ips_app.infrastructure.repository.firmware.beanie_model import FirmwareDocument


class GridFsFirmwareRepository(FirmwareRepository):
    def __init__(self, bucket: AsyncIOMotorGridFSBucket) -> None:
        self.bucket = bucket

    async def create_firmware(
        self,
        version: str,
        board_variant: str,
        content: bytes,
        checksum: str,
        created_by: Optional[Any] = None,
        session: Optional[Any] = None,
    ) -> Firmware:
        try:
            actual_checksum = hashlib.sha256(content).hexdigest()
            if actual_checksum != checksum.lower():
                raise ValidatorDomainException(
                    "Uploaded file checksum does not match the provided checksum."
                )

            file_id = await self.bucket.upload_from_stream(
                f"{version}-{board_variant}.bin", content
            )

            doc = FirmwareDocument(
                version=version,
                board_variant=board_variant,
                size=len(content),
                checksum=actual_checksum,
                file_id=file_id,
                created_by=created_by,
            )
            await doc.insert(session=session)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_firmware_by_id(self, id: Any, session: Optional[Any] = None) -> Firmware:
        try:
            doc = await self._read_firmware_document(id, session)
            return doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_firmwares_by_pagination(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        session: Optional[Any] = None,
    ) -> Tuple[List[Firmware], int]:
        try:
            query_filter = {}
            if search:
                query_filter = {
                    "$or": [
                        {"version": {"$regex": search, "$options": "i"}},
                        {"board_variant": {"$regex": search, "$options": "i"}},
                    ]
                }

            query = FirmwareDocument.find(query_filter, session=session)
            return await paginate(query, page, limit, FirmwareDocument.to_domain)
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def read_firmware_content_by_id(
        self, id: Any, session: Optional[Any] = None
    ) -> Tuple[bytes, Firmware]:
        try:
            doc = await self._read_firmware_document(id, session)
            stream = await self.bucket.open_download_stream(doc.file_id)
            content = await stream.read()
            return content, doc.to_domain()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def delete_firmware_by_id(self, id: Any, session: Optional[Any] = None) -> None:
        try:
            doc = await self._read_firmware_document(id, session)
            await self.bucket.delete(doc.file_id)
            await doc.delete(session=session)
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    async def _read_firmware_document(
        self, id: Any, session: Optional[Any]
    ) -> FirmwareDocument:
        doc = await get_by_id(FirmwareDocument, id, session=session)
        if not doc:
            raise NotFoundDomainException(f"Firmware '{id}' not found")
        return doc
