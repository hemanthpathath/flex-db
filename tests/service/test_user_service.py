"""
Tests for UserService.
"""

import pytest

from app.repository.errors import NotFoundError


@pytest.mark.asyncio
async def test_create_user(user_service):
    """Test creating a user."""
    user = await user_service.create("test@example.com", "Test User")
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.display_name == "Test User"


@pytest.mark.asyncio
async def test_create_user_missing_email(user_service):
    """Test creating a user without email raises ValueError."""
    with pytest.raises(ValueError, match="email is required"):
        await user_service.create("", "Test User")


@pytest.mark.asyncio
async def test_create_user_missing_display_name(user_service):
    """Test creating a user without display_name raises ValueError."""
    with pytest.raises(ValueError, match="display_name is required"):
        await user_service.create("test@example.com", "")


@pytest.mark.asyncio
async def test_get_user_by_id(user_service):
    """Test retrieving a user by ID."""
    created = await user_service.create("test@example.com", "Test User")
    
    retrieved = await user_service.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.email == created.email


@pytest.mark.asyncio
async def test_update_user(user_service):
    """Test updating a user."""
    created = await user_service.create("test@example.com", "Test User")
    
    updated = await user_service.update(
        created.id,
        email="updated@example.com",
        display_name="Updated User"
    )
    
    assert updated.email == "updated@example.com"
    assert updated.display_name == "Updated User"


@pytest.mark.asyncio
async def test_update_user_partial(user_service):
    """Test updating a user with partial fields."""
    created = await user_service.create("test@example.com", "Test User")
    
    updated = await user_service.update(
        created.id,
        email="",
        display_name="Updated Name Only"
    )
    
    assert updated.email == "test@example.com"  # Unchanged
    assert updated.display_name == "Updated Name Only"


@pytest.mark.asyncio
async def test_delete_user(user_service):
    """Test deleting a user."""
    created = await user_service.create("test@example.com", "Test User")
    
    await user_service.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await user_service.get_by_id(created.id)


@pytest.mark.asyncio
async def test_add_user_to_tenant(user_service, tenant_service):
    """Test adding a user to a tenant."""
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    tenant = await tenant_service.create(unique_slug, "Test Tenant")
    user = await user_service.create("test@example.com", "Test User")
    
    tenant_user = await user_service.add_to_tenant(tenant.id, user.id, "admin")
    
    assert tenant_user.tenant_id == tenant.id
    assert tenant_user.user_id == user.id
    assert tenant_user.role == "admin"


@pytest.mark.asyncio
async def test_remove_user_from_tenant(user_service, tenant_service):
    """Test removing a user from a tenant."""
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    tenant = await tenant_service.create(unique_slug, "Test Tenant")
    user = await user_service.create("test@example.com", "Test User")
    
    await user_service.add_to_tenant(tenant.id, user.id, "member")
    await user_service.remove_from_tenant(tenant.id, user.id)
    
    # Verify removal by checking list is empty
    tenant_users, _ = await user_service.list_tenant_users(tenant.id, page_size=10, page_token="")
    assert len(tenant_users) == 0


@pytest.mark.asyncio
async def test_list_tenant_users(user_service, tenant_service):
    """Test listing users in a tenant."""
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    tenant = await tenant_service.create(unique_slug, "Test Tenant")
    
    # Create and add multiple users
    for i in range(3):
        user = await user_service.create(f"user{i}@example.com", f"User {i}")
        await user_service.add_to_tenant(tenant.id, user.id, "member")
    
    tenant_users, result = await user_service.list_tenant_users(tenant.id, page_size=10, page_token="")
    
    assert len(tenant_users) == 3
    assert result.total_count == 3

