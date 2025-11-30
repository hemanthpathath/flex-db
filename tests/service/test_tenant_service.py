"""
Tests for TenantService.
"""

import pytest

from app.repository.errors import NotFoundError


@pytest.mark.asyncio
async def test_create_tenant(tenant_service):
    """Test creating a tenant."""
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    tenant = await tenant_service.create(unique_slug, "Test Tenant")
    
    assert tenant.id is not None
    assert tenant.slug == unique_slug
    assert tenant.name == "Test Tenant"
    assert tenant.status == "active"


@pytest.mark.asyncio
async def test_create_tenant_missing_slug(tenant_service):
    """Test creating a tenant without slug raises ValueError."""
    with pytest.raises(ValueError, match="slug is required"):
        await tenant_service.create("", "Test Tenant")


@pytest.mark.asyncio
async def test_create_tenant_missing_name(tenant_service):
    """Test creating a tenant without name raises ValueError."""
    with pytest.raises(ValueError, match="name is required"):
        await tenant_service.create("test-tenant", "")


@pytest.mark.asyncio
async def test_get_tenant_by_id(tenant_service):
    """Test retrieving a tenant by ID."""
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    created = await tenant_service.create(unique_slug, "Test Tenant")
    
    retrieved = await tenant_service.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.slug == created.slug


@pytest.mark.asyncio
async def test_get_tenant_not_found(tenant_service):
    """Test retrieving a non-existent tenant raises NotFoundError."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    with pytest.raises(NotFoundError):
        await tenant_service.get_by_id(non_existent_id)


@pytest.mark.asyncio
async def test_update_tenant(tenant_service):
    """Test updating a tenant."""
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    created = await tenant_service.create(unique_slug, "Test Tenant")
    
    updated = await tenant_service.update(
        created.id,
        slug="updated-tenant",
        name="Updated Tenant",
        status="inactive"
    )
    
    assert updated.slug == "updated-tenant"
    assert updated.name == "Updated Tenant"
    assert updated.status == "inactive"


@pytest.mark.asyncio
async def test_update_tenant_partial(tenant_service):
    """Test updating a tenant with partial fields."""
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    created = await tenant_service.create(unique_slug, "Test Tenant")
    
    updated = await tenant_service.update(
        created.id,
        slug="",
        name="Updated Name Only",
        status=""
    )
    
    assert updated.slug == unique_slug  # Unchanged
    assert updated.name == "Updated Name Only"
    assert updated.status == "active"  # Unchanged


@pytest.mark.asyncio
async def test_delete_tenant(tenant_service):
    """Test deleting a tenant."""
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    created = await tenant_service.create(unique_slug, "Test Tenant")
    
    await tenant_service.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await tenant_service.get_by_id(created.id)


@pytest.mark.asyncio
async def test_list_tenants(tenant_service):
    """Test listing tenants with pagination."""
    import uuid
    # Create multiple tenants
    for i in range(5):
        unique_slug = f"tenant-{i}-{uuid.uuid4().hex[:8]}"
        await tenant_service.create(unique_slug, f"Tenant {i}")
    
    tenants, result = await tenant_service.list(page_size=10, page_token="")
    
    assert len(tenants) == 5
    assert result.total_count == 5


@pytest.mark.asyncio
async def test_list_tenants_pagination(tenant_service):
    """Test listing tenants with pagination."""
    import uuid
    # Create multiple tenants
    for i in range(15):
        unique_slug = f"tenant-{i}-{uuid.uuid4().hex[:8]}"
        await tenant_service.create(unique_slug, f"Tenant {i}")
    
    # First page
    tenants1, result1 = await tenant_service.list(page_size=5, page_token="")
    
    assert len(tenants1) == 5
    assert result1.total_count == 15
    assert result1.next_page_token == "5"

