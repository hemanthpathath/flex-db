"""
Tests for REST wrapper forwarding logic.

These tests mock the JSON-RPC client to verify that:
1. REST endpoints correctly forward requests to JSON-RPC backend
2. Request parameters are properly mapped
3. JSON-RPC responses are correctly returned
4. Errors are properly handled
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from rest_wrapper.main import app
from rest_wrapper.client import JSONRPCError


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_rpc_client():
    """Create a mock JSON-RPC client."""
    with patch("rest_wrapper.routers.tenants.get_client") as mock_tenants, \
         patch("rest_wrapper.routers.users.get_client") as mock_users, \
         patch("rest_wrapper.routers.node_types.get_client") as mock_node_types, \
         patch("rest_wrapper.routers.nodes.get_client") as mock_nodes, \
         patch("rest_wrapper.routers.relationships.get_client") as mock_relationships:
        
        mock_client = AsyncMock()
        mock_tenants.return_value = mock_client
        mock_users.return_value = mock_client
        mock_node_types.return_value = mock_client
        mock_nodes.return_value = mock_client
        mock_relationships.return_value = mock_client
        
        yield mock_client


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestTenantEndpoints:
    """Tests for tenant endpoints."""
    
    def test_create_tenant(self, client, mock_rpc_client):
        """Test create tenant forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {
            "tenant": {
                "id": "test-id",
                "slug": "test-tenant",
                "name": "Test Tenant",
                "status": "active",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        
        response = client.post("/tenants", json={
            "slug": "test-tenant",
            "name": "Test Tenant",
        })
        
        assert response.status_code == 201
        assert response.json()["tenant"]["slug"] == "test-tenant"
        mock_rpc_client.call.assert_called_once_with(
            "create_tenant",
            {"slug": "test-tenant", "name": "Test Tenant"}
        )
    
    def test_get_tenant(self, client, mock_rpc_client):
        """Test get tenant forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {
            "tenant": {
                "id": "test-id",
                "slug": "test-tenant",
                "name": "Test Tenant",
                "status": "active",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        
        response = client.get("/tenants/test-id")
        
        assert response.status_code == 200
        assert response.json()["tenant"]["id"] == "test-id"
        mock_rpc_client.call.assert_called_once_with("get_tenant", {"id": "test-id"})
    
    def test_get_tenant_not_found(self, client, mock_rpc_client):
        """Test get tenant returns 404 for not found."""
        mock_rpc_client.call.side_effect = JSONRPCError(-32001, "Tenant not found")
        
        response = client.get("/tenants/nonexistent")
        
        assert response.status_code == 404
    
    def test_update_tenant(self, client, mock_rpc_client):
        """Test update tenant forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {
            "tenant": {
                "id": "test-id",
                "slug": "updated-tenant",
                "name": "Updated Tenant",
                "status": "active",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        
        response = client.put("/tenants/test-id", json={
            "slug": "updated-tenant",
            "name": "Updated Tenant",
        })
        
        assert response.status_code == 200
        assert response.json()["tenant"]["slug"] == "updated-tenant"
    
    def test_delete_tenant(self, client, mock_rpc_client):
        """Test delete tenant forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {}
        
        response = client.delete("/tenants/test-id")
        
        assert response.status_code == 204
        mock_rpc_client.call.assert_called_once_with("delete_tenant", {"id": "test-id"})
    
    def test_list_tenants(self, client, mock_rpc_client):
        """Test list tenants forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {
            "tenants": [
                {
                    "id": "test-id",
                    "slug": "test-tenant",
                    "name": "Test Tenant",
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                }
            ],
            "pagination": {"next_page_token": "", "total_count": 1},
        }
        
        response = client.get("/tenants?page_size=10")
        
        assert response.status_code == 200
        assert len(response.json()["tenants"]) == 1


class TestUserEndpoints:
    """Tests for user endpoints."""
    
    def test_create_user(self, client, mock_rpc_client):
        """Test create user forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {
            "user": {
                "id": "user-id",
                "email": "test@example.com",
                "display_name": "Test User",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        
        response = client.post("/users", json={
            "email": "test@example.com",
            "display_name": "Test User",
        })
        
        assert response.status_code == 201
        assert response.json()["user"]["email"] == "test@example.com"
    
    def test_get_user(self, client, mock_rpc_client):
        """Test get user forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {
            "user": {
                "id": "user-id",
                "email": "test@example.com",
                "display_name": "Test User",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        
        response = client.get("/users/user-id")
        
        assert response.status_code == 200
        assert response.json()["user"]["id"] == "user-id"


class TestNodeTypeEndpoints:
    """Tests for node type endpoints."""
    
    def test_create_node_type(self, client, mock_rpc_client):
        """Test create node type forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {
            "node_type": {
                "id": "node-type-id",
                "tenant_id": "tenant-id",
                "name": "Task",
                "description": "A task",
                "schema": "{}",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        
        response = client.post("/tenants/tenant-id/node-types", json={
            "name": "Task",
            "description": "A task",
        })
        
        assert response.status_code == 201
        assert response.json()["node_type"]["name"] == "Task"


class TestNodeEndpoints:
    """Tests for node endpoints."""
    
    def test_create_node(self, client, mock_rpc_client):
        """Test create node forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {
            "node": {
                "id": "node-id",
                "tenant_id": "tenant-id",
                "node_type_id": "node-type-id",
                "data": '{"title": "Test"}',
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        
        response = client.post("/tenants/tenant-id/nodes", json={
            "node_type_id": "node-type-id",
            "data": '{"title": "Test"}',
        })
        
        assert response.status_code == 201
        assert response.json()["node"]["id"] == "node-id"


class TestRelationshipEndpoints:
    """Tests for relationship endpoints."""
    
    def test_create_relationship(self, client, mock_rpc_client):
        """Test create relationship forwards to JSON-RPC."""
        mock_rpc_client.call.return_value = {
            "relationship": {
                "id": "rel-id",
                "tenant_id": "tenant-id",
                "source_node_id": "source-id",
                "target_node_id": "target-id",
                "relationship_type": "depends_on",
                "data": "{}",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        
        response = client.post("/tenants/tenant-id/relationships", json={
            "source_node_id": "source-id",
            "target_node_id": "target-id",
            "relationship_type": "depends_on",
        })
        
        assert response.status_code == 201
        assert response.json()["relationship"]["relationship_type"] == "depends_on"


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_invalid_params_returns_400(self, client, mock_rpc_client):
        """Test invalid params error returns 400."""
        mock_rpc_client.call.side_effect = JSONRPCError(-32602, "Invalid parameters")
        
        response = client.post("/tenants", json={
            "slug": "test",
            "name": "Test",
        })
        
        assert response.status_code == 400
    
    def test_not_found_returns_404(self, client, mock_rpc_client):
        """Test not found error returns 404."""
        mock_rpc_client.call.side_effect = JSONRPCError(-32001, "Not found")
        
        response = client.get("/tenants/nonexistent")
        
        assert response.status_code == 404
    
    def test_internal_error_returns_500(self, client, mock_rpc_client):
        """Test internal error returns 500."""
        mock_rpc_client.call.side_effect = JSONRPCError(-32603, "Internal error")
        
        response = client.get("/tenants/some-id")
        
        assert response.status_code == 500


class TestOpenAPI:
    """Tests for OpenAPI documentation."""
    
    def test_openapi_schema_available(self, client):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
    
    def test_swagger_ui_available(self, client):
        """Test Swagger UI is available."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_available(self, client):
        """Test ReDoc is available."""
        response = client.get("/redoc")
        assert response.status_code == 200
