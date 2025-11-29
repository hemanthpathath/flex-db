"""
Node REST API router.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from rest_wrapper.client import get_client, JSONRPCError
from rest_wrapper.models import (
    NodeCreate,
    NodeUpdate,
    NodeResponse,
    NodeListResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/tenants/{tenant_id}/nodes", tags=["Nodes"])


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
    response_model=NodeResponse,
    status_code=201,
    summary="Create a node",
    description="Create a new node within a tenant.",
    responses={
        201: {"description": "Node created successfully"},
        400: {"description": "Invalid parameters", "model": ErrorResponse},
        404: {"description": "Tenant or node type not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def create_node(tenant_id: str, node: NodeCreate):
    """Create a new node."""
    try:
        client = get_client()
        result = await client.call("create_node", {
            "tenant_id": tenant_id,
            "node_type_id": node.node_type_id,
            "data": node.data or "{}",
        })
        return result
    except JSONRPCError as e:
        raise _handle_rpc_error(e)


@router.get(
    "/{node_id}",
    response_model=NodeResponse,
    summary="Get a node",
    description="Get a node by its ID within a tenant.",
    responses={
        200: {"description": "Node found"},
        404: {"description": "Node or tenant not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def get_node(tenant_id: str, node_id: str):
    """Get a node by ID."""
    try:
        client = get_client()
        result = await client.call("get_node", {
            "id": node_id,
            "tenant_id": tenant_id,
        })
        return result
    except JSONRPCError as e:
        raise _handle_rpc_error(e)


@router.put(
    "/{node_id}",
    response_model=NodeResponse,
    summary="Update a node",
    description="Update an existing node. Only provided fields will be updated.",
    responses={
        200: {"description": "Node updated successfully"},
        400: {"description": "Invalid parameters", "model": ErrorResponse},
        404: {"description": "Node or tenant not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def update_node(tenant_id: str, node_id: str, node: NodeUpdate):
    """Update an existing node."""
    try:
        client = get_client()
        params = {"id": node_id, "tenant_id": tenant_id}
        if node.data is not None:
            params["data"] = node.data
        result = await client.call("update_node", params)
        return result
    except JSONRPCError as e:
        raise _handle_rpc_error(e)


@router.delete(
    "/{node_id}",
    status_code=204,
    summary="Delete a node",
    description="Delete a node by its ID.",
    responses={
        204: {"description": "Node deleted successfully"},
        404: {"description": "Node or tenant not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def delete_node(tenant_id: str, node_id: str):
    """Delete a node."""
    try:
        client = get_client()
        await client.call("delete_node", {
            "id": node_id,
            "tenant_id": tenant_id,
        })
        return None
    except JSONRPCError as e:
        raise _handle_rpc_error(e)


@router.get(
    "",
    response_model=NodeListResponse,
    summary="List nodes",
    description="List all nodes within a tenant with optional filtering by node type.",
    responses={
        200: {"description": "List of nodes"},
        404: {"description": "Tenant not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
)
async def list_nodes(
    tenant_id: str,
    node_type_id: Optional[str] = Query(default=None, description="Filter by node type ID"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    page_token: str = Query(default="", description="Token for the next page"),
):
    """List nodes for a tenant."""
    try:
        client = get_client()
        params = {
            "tenant_id": tenant_id,
            "pagination": {"page_size": page_size, "page_token": page_token},
        }
        if node_type_id:
            params["node_type_id"] = node_type_id
        result = await client.call("list_nodes", params)
        return result
    except JSONRPCError as e:
        raise _handle_rpc_error(e)
