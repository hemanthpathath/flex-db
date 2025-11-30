"""
Tests for JSON-RPC handlers.
"""

import json
import pytest
from httpx import AsyncClient

from app.jsonrpc.handlers import register_methods
from app.service import TenantService, UserService


@pytest.mark.asyncio
async def test_jsonrpc_create_tenant(async_client: AsyncClient, tenant_service: TenantService, user_service: UserService):
    """Test JSON-RPC create_tenant method."""
    # Register services
    register_methods(tenant_service, user_service)
    
    request = {
        "jsonrpc": "2.0",
        "method": "create_tenant",
        "params": {"slug": "test-tenant", "name": "Test Tenant"},
        "id": 1
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert "tenant" in data["result"]
    assert data["result"]["tenant"]["slug"] == "test-tenant"
    assert data["result"]["tenant"]["name"] == "Test Tenant"
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_jsonrpc_get_tenant(async_client: AsyncClient, tenant_service: TenantService, user_service: UserService):
    """Test JSON-RPC get_tenant method."""
    register_methods(tenant_service, user_service)
    
    # Create tenant first
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    tenant = await tenant_service.create(unique_slug, "Test Tenant")
    
    request = {
        "jsonrpc": "2.0",
        "method": "get_tenant",
        "params": {"id": tenant.id},
        "id": 2
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert data["result"]["tenant"]["id"] == tenant.id
    assert data["result"]["tenant"]["slug"] == unique_slug


@pytest.mark.asyncio
async def test_jsonrpc_list_tenants(async_client: AsyncClient, tenant_service: TenantService, user_service: UserService):
    """Test JSON-RPC list_tenants method."""
    register_methods(tenant_service, user_service)
    
    # Create multiple tenants
    for i in range(3):
        await tenant_service.create(f"tenant-{i}", f"Tenant {i}")
    
    request = {
        "jsonrpc": "2.0",
        "method": "list_tenants",
        "params": {"pagination": {"page_size": 10, "page_token": ""}},
        "id": 3
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert len(data["result"]["tenants"]) == 3
    assert "pagination" in data["result"]


@pytest.mark.asyncio
async def test_jsonrpc_create_user(async_client: AsyncClient, tenant_service: TenantService, user_service: UserService):
    """Test JSON-RPC create_user method."""
    register_methods(tenant_service, user_service)
    
    request = {
        "jsonrpc": "2.0",
        "method": "create_user",
        "params": {"email": "test@example.com", "display_name": "Test User"},
        "id": 4
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert data["result"]["user"]["email"] == "test@example.com"
    assert data["result"]["user"]["display_name"] == "Test User"


@pytest.mark.asyncio
async def test_jsonrpc_error_not_found(async_client: AsyncClient, tenant_service: TenantService, user_service: UserService):
    """Test JSON-RPC error response for not found."""
    import uuid
    register_methods(tenant_service, user_service)
    
    non_existent_id = str(uuid.uuid4())
    request = {
        "jsonrpc": "2.0",
        "method": "get_tenant",
        "params": {"id": non_existent_id},
        "id": 5
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["error"]["code"] == -32001  # NotFoundError code


@pytest.mark.asyncio
async def test_jsonrpc_error_invalid_params(async_client: AsyncClient, tenant_service: TenantService, user_service: UserService):
    """Test JSON-RPC error response for invalid parameters."""
    register_methods(tenant_service, user_service)
    
    request = {
        "jsonrpc": "2.0",
        "method": "create_tenant",
        "params": {"slug": "", "name": "Test Tenant"},  # Empty slug
        "id": 6
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["error"]["code"] == -32602  # Invalid params


@pytest.mark.asyncio
async def test_jsonrpc_invalid_json(async_client: AsyncClient):
    """Test JSON-RPC error response for invalid JSON.
    
    Note: jsonrpcserver may return 200 with an error response instead of 400,
    depending on how it handles parsing errors.
    """
    response = await async_client.post(
        "/jsonrpc",
        content="invalid json",
        headers={"Content-Type": "application/json"}
    )
    
    # jsonrpcserver might return 200 with error or 400 - accept either
    assert response.status_code in (200, 400)
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    # Parse error code is -32700
    assert data["error"]["code"] == -32700


@pytest.mark.asyncio
async def test_jsonrpc_method_not_found(async_client: AsyncClient):
    """Test JSON-RPC error response for method not found."""
    request = {
        "jsonrpc": "2.0",
        "method": "non_existent_method",
        "params": {},
        "id": 7
    }
    
    response = await async_client.post("/jsonrpc", json=request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["error"]["code"] == -32601  # Method not found

