"""
Tests for UserRepository.
"""

import pytest

from app.repository.errors import NotFoundError
from app.repository.models import User, TenantUser, ListOptions


@pytest.mark.asyncio
async def test_create_user(user_repo):
    """Test creating a user."""
    user = User(email="test@example.com", display_name="Test User")
    created = await user_repo.create(user)
    
    assert created.id is not None
    assert created.email == "test@example.com"
    assert created.display_name == "Test User"
    assert created.created_at is not None
    assert created.updated_at is not None


@pytest.mark.asyncio
async def test_get_user_by_id(user_repo):
    """Test retrieving a user by ID."""
    user = User(email="test@example.com", display_name="Test User")
    created = await user_repo.create(user)
    
    retrieved = await user_repo.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.email == created.email
    assert retrieved.display_name == created.display_name


@pytest.mark.asyncio
async def test_get_user_not_found(user_repo):
    """Test retrieving a non-existent user raises NotFoundError."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    with pytest.raises(NotFoundError):
        await user_repo.get_by_id(non_existent_id)


@pytest.mark.asyncio
async def test_update_user(user_repo):
    """Test updating a user."""
    user = User(email="test@example.com", display_name="Test User")
    created = await user_repo.create(user)
    
    created.email = "updated@example.com"
    created.display_name = "Updated User"
    
    updated = await user_repo.update(created)
    
    assert updated.email == "updated@example.com"
    assert updated.display_name == "Updated User"
    # Compare as timestamps to avoid timezone issues (use >= since timestamps might be same)
    assert updated.updated_at.timestamp() >= created.updated_at.timestamp()


@pytest.mark.asyncio
async def test_delete_user(user_repo):
    """Test deleting a user."""
    user = User(email="test@example.com", display_name="Test User")
    created = await user_repo.create(user)
    
    await user_repo.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await user_repo.get_by_id(created.id)


@pytest.mark.asyncio
async def test_list_users(user_repo):
    """Test listing users with pagination."""
    # Create multiple users
    for i in range(5):
        user = User(email=f"user{i}@example.com", display_name=f"User {i}")
        await user_repo.create(user)
    
    users, result = await user_repo.list(ListOptions(page_size=10, page_token=""))
    
    assert len(users) == 5
    assert result.total_count == 5


@pytest.mark.asyncio
async def test_add_user_to_tenant(user_repo, tenant_repo):
    """Test adding a user to a tenant."""
    from app.repository.models import Tenant
    
    # Create tenant and user
    tenant = Tenant(slug="test-tenant", name="Test Tenant")
    tenant = await tenant_repo.create(tenant)
    
    user = User(email="test@example.com", display_name="Test User")
    user = await user_repo.create(user)
    
    # Add user to tenant
    tenant_user = TenantUser(tenant_id=tenant.id, user_id=user.id, role="admin")
    result = await user_repo.add_to_tenant(tenant_user)
    
    assert result.tenant_id == tenant.id
    assert result.user_id == user.id
    assert result.role == "admin"
    assert result.status == "active"


@pytest.mark.asyncio
async def test_add_user_to_tenant_default_role(user_repo, tenant_repo):
    """Test adding a user to a tenant with default role."""
    from app.repository.models import Tenant
    
    tenant = Tenant(slug="test-tenant", name="Test Tenant")
    tenant = await tenant_repo.create(tenant)
    
    user = User(email="test@example.com", display_name="Test User")
    user = await user_repo.create(user)
    
    tenant_user = TenantUser(tenant_id=tenant.id, user_id=user.id)
    result = await user_repo.add_to_tenant(tenant_user)
    
    assert result.role == "member"


@pytest.mark.asyncio
async def test_remove_user_from_tenant(user_repo, tenant_repo):
    """Test removing a user from a tenant."""
    from app.repository.models import Tenant
    
    tenant = Tenant(slug="test-tenant", name="Test Tenant")
    tenant = await tenant_repo.create(tenant)
    
    user = User(email="test@example.com", display_name="Test User")
    user = await user_repo.create(user)
    
    tenant_user = TenantUser(tenant_id=tenant.id, user_id=user.id)
    await user_repo.add_to_tenant(tenant_user)
    
    await user_repo.remove_from_tenant(tenant.id, user.id)
    
    # Try to remove again - should raise NotFoundError
    with pytest.raises(NotFoundError):
        await user_repo.remove_from_tenant(tenant.id, user.id)


@pytest.mark.asyncio
async def test_list_tenant_users(user_repo, tenant_repo):
    """Test listing users in a tenant."""
    from app.repository.models import Tenant
    
    tenant = Tenant(slug="test-tenant", name="Test Tenant")
    tenant = await tenant_repo.create(tenant)
    
    # Create multiple users and add them to tenant
    for i in range(3):
        user = User(email=f"user{i}@example.com", display_name=f"User {i}")
        user = await user_repo.create(user)
        tenant_user = TenantUser(tenant_id=tenant.id, user_id=user.id)
        await user_repo.add_to_tenant(tenant_user)
    
    tenant_users, result = await user_repo.list_tenant_users(
        tenant.id, ListOptions(page_size=10, page_token="")
    )
    
    assert len(tenant_users) == 3
    assert result.total_count == 3

