"""
End-to-end API integration tests.
"""

import pytest
from httpx import AsyncClient

from app.jsonrpc.handlers import register_methods


@pytest.mark.asyncio
async def test_api_workflow(
    async_client: AsyncClient,
    tenant_service,
    user_service,
    test_tenant,
    test_user,
    test_node_type,
    test_node,
    test_relationship
):
    """Test complete API workflow: tenant -> user -> node_type -> node -> relationship."""
    # Register services
    register_methods(tenant_service, user_service)
    
    tenant_id = test_tenant["id"]
    user_id = test_user["id"]
    
    # Test: Add user to tenant
    request = {
        "jsonrpc": "2.0",
        "method": "add_user_to_tenant",
        "params": {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "role": "admin"
        },
        "id": 1
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"]["tenant_user"]["role"] == "admin"
    
    # Test: Create node type
    request = {
        "jsonrpc": "2.0",
        "method": "create_node_type",
        "params": {
            "tenant_id": tenant_id,
            "name": "Article",
            "description": "Blog article",
            "schema": '{"title": "string", "content": "string"}'
        },
        "id": 2
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    node_type_id = data["result"]["node_type"]["id"]
    
    # Test: Create node
    request = {
        "jsonrpc": "2.0",
        "method": "create_node",
        "params": {
            "tenant_id": tenant_id,
            "node_type_id": node_type_id,
            "data": '{"title": "Hello World", "content": "My first article"}'
        },
        "id": 3
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    node_id = data["result"]["node"]["id"]
    
    # Test: Create second node for relationship
    request = {
        "jsonrpc": "2.0",
        "method": "create_node",
        "params": {
            "tenant_id": tenant_id,
            "node_type_id": node_type_id,
            "data": '{"title": "Second Article", "content": "Another article"}'
        },
        "id": 4
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    node_id_2 = data["result"]["node"]["id"]
    
    # Test: Create relationship
    request = {
        "jsonrpc": "2.0",
        "method": "create_relationship",
        "params": {
            "tenant_id": tenant_id,
            "source_node_id": node_id,
            "target_node_id": node_id_2,
            "relationship_type": "references",
            "data": '{"note": "reference"}'
        },
        "id": 5
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "relationship" in data["result"]
    relationship_id = data["result"]["relationship"]["id"]
    
    # Test: Get relationship
    request = {
        "jsonrpc": "2.0",
        "method": "get_relationship",
        "params": {
            "id": relationship_id,
            "tenant_id": tenant_id
        },
        "id": 6
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["relationship"]["id"] == relationship_id
    assert data["result"]["relationship"]["relationship_type"] == "references"
    
    # Test: List relationships
    request = {
        "jsonrpc": "2.0",
        "method": "list_relationships",
        "params": {
            "tenant_id": tenant_id,
            "pagination": {"page_size": 10, "page_token": ""}
        },
        "id": 7
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    assert len(data["result"]["relationships"]) >= 1


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test health check endpoint."""
    response = await async_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_openrpc_spec(async_client: AsyncClient):
    """Test OpenRPC specification endpoint."""
    response = await async_client.get("/openrpc.json")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check OpenRPC structure
    assert "openrpc" in data or "info" in data or "methods" in data
    # The response should be valid OpenRPC spec (either wrapped in openrpc key or direct)


@pytest.mark.asyncio
async def test_update_tenant_via_api(
    async_client: AsyncClient,
    tenant_service,
    user_service,
    test_tenant
):
    """Test updating tenant via API."""
    register_methods(tenant_service, user_service)
    
    tenant_id = test_tenant["id"]
    
    request = {
        "jsonrpc": "2.0",
        "method": "update_tenant",
        "params": {
            "id": tenant_id,
            "slug": "updated-tenant",
            "name": "Updated Tenant",
            "status": "inactive"
        },
        "id": 1
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    
    assert data["result"]["tenant"]["slug"] == "updated-tenant"
    assert data["result"]["tenant"]["name"] == "Updated Tenant"
    assert data["result"]["tenant"]["status"] == "inactive"


@pytest.mark.asyncio
async def test_delete_tenant_via_api(
    async_client: AsyncClient,
    tenant_service,
    user_service
):
    """Test deleting tenant via API."""
    register_methods(tenant_service, user_service)
    
    # Create tenant
    tenant = await tenant_service.create("to-delete", "To Delete")
    
    request = {
        "jsonrpc": "2.0",
        "method": "delete_tenant",
        "params": {"id": tenant.id},
        "id": 1
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    
    # Verify tenant is deleted
    request = {
        "jsonrpc": "2.0",
        "method": "get_tenant",
        "params": {"id": tenant.id},
        "id": 2
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    assert "error" in data  # Should return error for deleted tenant


@pytest.mark.asyncio
async def test_list_nodes_with_filter(
    async_client: AsyncClient,
    tenant_service,
    user_service,
    test_tenant,
    test_node_type
):
    """Test listing nodes with node_type filter."""
    register_methods(tenant_service, user_service)
    
    tenant_id = test_tenant["id"]
    node_type_id = test_node_type["id"]
    
    request = {
        "jsonrpc": "2.0",
        "method": "list_nodes",
        "params": {
            "tenant_id": tenant_id,
            "node_type_id": node_type_id,
            "pagination": {"page_size": 10, "page_token": ""}
        },
        "id": 1
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    assert response.status_code == 200
    data = response.json()
    
    assert "nodes" in data["result"]
    assert "pagination" in data["result"]
    # All returned nodes should be of the specified type
    for node in data["result"]["nodes"]:
        assert node["node_type_id"] == node_type_id

