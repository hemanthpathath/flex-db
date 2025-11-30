"""
Tests for TenantRepository.
"""

import pytest

from app.repository.errors import NotFoundError
from app.repository.models import Tenant, ListOptions


@pytest.mark.asyncio
async def test_create_tenant(tenant_repo):
    """Test creating a tenant."""
    tenant = Tenant(slug="test-tenant", name="Test Tenant")
    created = await tenant_repo.create(tenant)
    
    assert created.id is not None
    assert created.slug == "test-tenant"
    assert created.name == "Test Tenant"
    assert created.status == "active"
    assert created.created_at is not None
    assert created.updated_at is not None


@pytest.mark.asyncio
async def test_get_tenant_by_id(tenant_repo):
    """Test retrieving a tenant by ID."""
    tenant = Tenant(slug="test-tenant", name="Test Tenant")
    created = await tenant_repo.create(tenant)
    
    retrieved = await tenant_repo.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.slug == created.slug
    assert retrieved.name == created.name


@pytest.mark.asyncio
async def test_get_tenant_not_found(tenant_repo):
    """Test retrieving a non-existent tenant raises NotFoundError."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    with pytest.raises(NotFoundError):
        await tenant_repo.get_by_id(non_existent_id)


@pytest.mark.asyncio
async def test_update_tenant(tenant_repo):
    """Test updating a tenant."""
    tenant = Tenant(slug="test-tenant", name="Test Tenant")
    created = await tenant_repo.create(tenant)
    
    created.slug = "updated-tenant"
    created.name = "Updated Tenant"
    created.status = "inactive"
    
    updated = await tenant_repo.update(created)
    
    assert updated.slug == "updated-tenant"
    assert updated.name == "Updated Tenant"
    assert updated.status == "inactive"
    # Compare as timestamps to avoid timezone issues (use >= since timestamps might be same)
    assert updated.updated_at.timestamp() >= created.updated_at.timestamp()


@pytest.mark.asyncio
async def test_update_tenant_not_found(tenant_repo):
    """Test updating a non-existent tenant raises NotFoundError."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    tenant = Tenant(id=non_existent_id, slug="test", name="Test")
    
    with pytest.raises(NotFoundError):
        await tenant_repo.update(tenant)


@pytest.mark.asyncio
async def test_delete_tenant(tenant_repo):
    """Test deleting a tenant."""
    tenant = Tenant(slug="test-tenant", name="Test Tenant")
    created = await tenant_repo.create(tenant)
    
    await tenant_repo.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await tenant_repo.get_by_id(created.id)


@pytest.mark.asyncio
async def test_delete_tenant_not_found(tenant_repo):
    """Test deleting a non-existent tenant raises NotFoundError."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    with pytest.raises(NotFoundError):
        await tenant_repo.delete(non_existent_id)


@pytest.mark.asyncio
async def test_list_tenants(tenant_repo):
    """Test listing tenants with pagination."""
    # Create multiple tenants
    for i in range(5):
        tenant = Tenant(slug=f"tenant-{i}", name=f"Tenant {i}")
        await tenant_repo.create(tenant)
    
    # List all tenants
    tenants, result = await tenant_repo.list(ListOptions(page_size=10, page_token=""))
    
    assert len(tenants) == 5
    assert result.total_count == 5


@pytest.mark.asyncio
async def test_list_tenants_pagination(tenant_repo):
    """Test listing tenants with pagination."""
    # Create multiple tenants
    for i in range(15):
        tenant = Tenant(slug=f"tenant-{i}", name=f"Tenant {i}")
        await tenant_repo.create(tenant)
    
    # First page
    tenants1, result1 = await tenant_repo.list(ListOptions(page_size=5, page_token=""))
    
    assert len(tenants1) == 5
    assert result1.total_count == 15
    assert result1.next_page_token == "5"
    
    # Second page
    tenants2, result2 = await tenant_repo.list(ListOptions(page_size=5, page_token="5"))
    
    assert len(tenants2) == 5
    assert tenants1[0].id != tenants2[0].id  # Different tenants


@pytest.mark.asyncio
async def test_list_tenants_empty(tenant_repo):
    """Test listing tenants when none exist."""
    tenants, result = await tenant_repo.list(ListOptions(page_size=10, page_token=""))
    
    assert len(tenants) == 0
    assert result.total_count == 0
    assert result.next_page_token == ""

