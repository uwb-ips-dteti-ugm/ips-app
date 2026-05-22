from typing import Optional, Union

from fastapi import status
from fastapi.responses import JSONResponse

from ips_app.controllers.http.dto.common import ErrorResponse, MessageResponse
from ips_app.controllers.http.dto.node_network import (
    AddNodeNetworkRequest,
    NodeNetworkResponse,
    NodeNetworksResponse,
    SetNodeNetworkRequest,
)
from ips_app.controllers.http.middlewares.auth_jwt import get_claims
from ips_app.domain.models.exception import (
    DuplicateDomainException,
    ForbiddenDomainException,
    NotFoundDomainException,
    UnexpectedDomainException,
    ValidatorDomainException,
)
from ips_app.domain.ports.driving.http.node_network import NodeNetworkHTTP


class NodeNetworkHandler:
    def __init__(self, service: NodeNetworkHTTP):
        self.service = service

    async def post_node_network(
        self,
        request: AddNodeNetworkRequest,
    ) -> Union[NodeNetworkResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            node_network = await self.service.add_node_network(
                pan_id=request.pan_id,
                name=request.name,
                description=request.description,
                created_by=claims.user_id if claims else None,
            )
            return NodeNetworkResponse.from_domain(node_network)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, DuplicateDomainException):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content=ErrorResponse(
                        error="A node network with this PAN ID already exists. Please choose another PAN ID."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while creating the node network. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while creating the node network. Please try again."
                ).model_dump(),
            )

    async def get_node_network(
        self,
        node_network_id: str,
    ) -> Union[NodeNetworkResponse, JSONResponse]:
        try:
            node_network = await self.service.get_node_network(node_network_id)
            return NodeNetworkResponse.from_domain(node_network)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(error="Node network not found.").model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading the node network. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the node network. Please try again."
                ).model_dump(),
            )

    async def get_node_network_by_pan_id(
        self,
        pan_id: int,
    ) -> Union[NodeNetworkResponse, JSONResponse]:
        try:
            node_network = await self.service.get_node_network_by_pan_id(pan_id)
            return NodeNetworkResponse.from_domain(node_network)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="No node network uses this PAN ID."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading the node network. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading the node network. Please try again."
                ).model_dump(),
            )

    async def get_node_networks(
        self,
        page: int = 0,
        limit: int = 10,
        cursor_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Union[NodeNetworksResponse, JSONResponse]:
        try:
            items, total = await self.service.get_node_networks(
                page=page,
                limit=limit,
                cursor_id=cursor_id,
                search=search,
            )
            return NodeNetworksResponse.from_domain(
                items=items,
                page=page,
                limit=limit,
                total=total,
            )
        except Exception as e:
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while loading node networks. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while loading node networks. Please try again."
                ).model_dump(),
            )

    async def patch_node_network(
        self,
        node_network_id: str,
        request: SetNodeNetworkRequest,
    ) -> Union[NodeNetworkResponse, JSONResponse]:
        try:
            claims = get_claims()
            request.validate_fields()
            node_network = await self.service.set_node_network(
                node_network_id=node_network_id,
                pan_id=request.pan_id,
                name=request.name,
                description=request.description,
                updated_by=claims.user_id if claims else None,
            )
            return NodeNetworkResponse.from_domain(node_network)
        except Exception as e:
            if isinstance(e, ValidatorDomainException):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(error=str(e)).model_dump(),
                )
            if isinstance(e, DuplicateDomainException):
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content=ErrorResponse(
                        error="A node network with this PAN ID already exists. Please choose another PAN ID."
                    ).model_dump(),
                )
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The node network you want to update does not exist."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while updating the node network. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while updating the node network. Please try again."
                ).model_dump(),
            )

    async def delete_node_network(
        self,
        node_network_id: str,
    ) -> Union[MessageResponse, JSONResponse]:
        try:
            message = await self.service.remove_node_network(node_network_id)
            return MessageResponse(message=message)
        except Exception as e:
            if isinstance(e, NotFoundDomainException):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=ErrorResponse(
                        error="The node network you want to delete does not exist."
                    ).model_dump(),
                )
            if isinstance(e, ForbiddenDomainException):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error="This node network cannot be deleted because one or more nodes still use it."
                    ).model_dump(),
                )
            if isinstance(e, UnexpectedDomainException):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=ErrorResponse(
                        error="Something went wrong while deleting the node network. Please try again."
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Something went wrong while deleting the node network. Please try again."
                ).model_dump(),
            )
