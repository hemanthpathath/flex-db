"""
Relationship REST API router.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from rest_wrapper.client import get_client, JSONRPCError
from rest_wrapper.models import (
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipResponse,
    RelationshipListResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/tenants/{tenant_id}/relationships", tags=["Relationships"])


def _handle_rpc_error(e: JSONRPCError) -> HTTPException:
    """Convert JSON-RPC error to HTTP exception."""
    if e.code == -32001:  # Not found
        return HTTPException(status_code=404, detail=e.message)
    elif e.code == -32602:  # Invalid params
        return HTTPException(status_code=400, detail=e.message)
    else:
        return HTTPException(status_code=500, detail=e.message)


@router.post(
    "",
    response_model=RelationshipResponse,
    status_code=201,
    summary="Create a relationship",
    description="Create a new relationship between two nodes within a tenant.",
    responses={
        201: {"description": "Relationship created successfully"},
        400: {"description": "Invalid parameters", "model": ErrorResponse},
        404: {"description": "Tenant or nodes not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def create_relationship(tenant_id: str, relationship: RelationshipCreate):
    """Create a new relationship."""
    try:
        client = get_client()
        result = await client.call("create_relationship", {
            "tenant_id": tenant_id,
            "source_node_id": relationship.source_node_id,
            "target_node_id": relationship.target_node_id,
            "relationship_type": relationship.relationship_type,
            "data": relationship.data or "{}",
        })
        return result
    except JSONRPCError as e:
        raise _handle_rpc_error(e)


@router.get(
    "/{relationship_id}",
    response_model=RelationshipResponse,
    summary="Get a relationship",
    description="Get a relationship by its ID within a tenant.",
    responses={
        200: {"description": "Relationship found"},
        404: {"description": "Relationship or tenant not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def get_relationship(tenant_id: str, relationship_id: str):
    """Get a relationship by ID."""
    try:
        client = get_client()
        result = await client.call("get_relationship", {
            "id": relationship_id,
            "tenant_id": tenant_id,
        })
        return result
    except JSONRPCError as e:
        raise _handle_rpc_error(e)


@router.put(
    "/{relationship_id}",
    response_model=RelationshipResponse,
    summary="Update a relationship",
    description="Update an existing relationship. Only provided fields will be updated.",
    responses={
        200: {"description": "Relationship updated successfully"},
        400: {"description": "Invalid parameters", "model": ErrorResponse},
        404: {"description": "Relationship or tenant not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def update_relationship(tenant_id: str, relationship_id: str, relationship: RelationshipUpdate):
    """Update an existing relationship."""
    try:
        client = get_client()
        params = {"id": relationship_id, "tenant_id": tenant_id}
        if relationship.relationship_type is not None:
            params["relationship_type"] = relationship.relationship_type
        if relationship.data is not None:
            params["data"] = relationship.data
        result = await client.call("update_relationship", params)
        return result
    except JSONRPCError as e:
        raise _handle_rpc_error(e)


@router.delete(
    "/{relationship_id}",
    status_code=204,
    summary="Delete a relationship",
    description="Delete a relationship by its ID.",
    responses={
        204: {"description": "Relationship deleted successfully"},
        404: {"description": "Relationship or tenant not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def delete_relationship(tenant_id: str, relationship_id: str):
    """Delete a relationship."""
    try:
        client = get_client()
        await client.call("delete_relationship", {
            "id": relationship_id,
            "tenant_id": tenant_id,
        })
        return None
    except JSONRPCError as e:
        raise _handle_rpc_error(e)


@router.get(
    "",
    response_model=RelationshipListResponse,
    summary="List relationships",
    description="List all relationships within a tenant with optional filtering.",
    responses={
        200: {"description": "List of relationships"},
        404: {"description": "Tenant not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def list_relationships(
    tenant_id: str,
    source_node_id: Optional[str] = Query(default=None, description="Filter by source node ID"),
    target_node_id: Optional[str] = Query(default=None, description="Filter by target node ID"),
    relationship_type: Optional[str] = Query(default=None, description="Filter by relationship type"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    page_token: str = Query(default="", description="Token for the next page"),
):
    """List relationships for a tenant."""
    try:
        client = get_client()
        params = {
            "tenant_id": tenant_id,
            "pagination": {"page_size": page_size, "page_token": page_token},
        }
        if source_node_id:
            params["source_node_id"] = source_node_id
        if target_node_id:
            params["target_node_id"] = target_node_id
        if relationship_type:
            params["relationship_type"] = relationship_type
        result = await client.call("list_relationships", params)
        return result
    except JSONRPCError as e:
        raise _handle_rpc_error(e)
