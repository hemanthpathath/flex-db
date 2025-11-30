"""
Tests for NodeTypeRepository.
"""

import pytest

from app.repository.errors import NotFoundError
from app.repository.models import NodeType, ListOptions


@pytest.mark.asyncio
async def test_create_node_type(nodetype_repo):
    """Test creating a node type."""
    schema = '{"title": "string", "content": "string"}'
    node_type = NodeType(name="Article", description="Blog article", schema=schema)
    created = await nodetype_repo.create(node_type)
    
    assert created.id is not None
    assert created.name == "Article"
    assert created.description == "Blog article"
    assert created.schema == schema
    assert created.created_at is not None
    assert created.updated_at is not None


@pytest.mark.asyncio
async def test_create_node_type_empty_schema(nodetype_repo):
    """Test creating a node type with empty schema."""
    node_type = NodeType(name="Article", description="Blog article", schema="")
    created = await nodetype_repo.create(node_type)
    
    assert created.id is not None
    assert created.name == "Article"
    assert created.schema == ""


@pytest.mark.asyncio
async def test_get_node_type_by_id(nodetype_repo):
    """Test retrieving a node type by ID."""
    schema = '{"title": "string"}'
    node_type = NodeType(name="Article", schema=schema)
    created = await nodetype_repo.create(node_type)
    
    retrieved = await nodetype_repo.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.name == created.name
    assert retrieved.schema == created.schema


@pytest.mark.asyncio
async def test_get_node_type_not_found(nodetype_repo):
    """Test retrieving a non-existent node type raises NotFoundError."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    with pytest.raises(NotFoundError):
        await nodetype_repo.get_by_id(non_existent_id)


@pytest.mark.asyncio
async def test_update_node_type(nodetype_repo):
    """Test updating a node type."""
    schema = '{"title": "string"}'
    node_type = NodeType(name="Article", schema=schema)
    created = await nodetype_repo.create(node_type)
    
    created.name = "Updated Article"
    created.description = "Updated description"
    created.schema = '{"title": "string", "author": "string"}'
    
    updated = await nodetype_repo.update(created)
    
    assert updated.name == "Updated Article"
    assert updated.description == "Updated description"
    assert updated.schema == '{"title": "string", "author": "string"}'
    # Compare as timestamps to avoid timezone issues
    assert updated.updated_at.timestamp() >= created.updated_at.timestamp()


@pytest.mark.asyncio
async def test_delete_node_type(nodetype_repo):
    """Test deleting a node type."""
    node_type = NodeType(name="Article", schema='{}')
    created = await nodetype_repo.create(node_type)
    
    await nodetype_repo.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await nodetype_repo.get_by_id(created.id)


@pytest.mark.asyncio
async def test_list_node_types(nodetype_repo):
    """Test listing node types with pagination."""
    # Create multiple node types
    for i in range(5):
        node_type = NodeType(name=f"Type {i}", schema='{}')
        await nodetype_repo.create(node_type)
    
    node_types, result = await nodetype_repo.list(ListOptions(page_size=10, page_token=""))
    
    assert len(node_types) == 5
    assert result.total_count == 5


@pytest.mark.asyncio
async def test_list_node_types_pagination(nodetype_repo):
    """Test listing node types with pagination."""
    # Create multiple node types
    for i in range(15):
        node_type = NodeType(name=f"Type {i}", schema='{}')
        await nodetype_repo.create(node_type)
    
    # First page
    node_types1, result1 = await nodetype_repo.list(ListOptions(page_size=5, page_token=""))
    
    assert len(node_types1) == 5
    assert result1.total_count == 15
    assert result1.next_page_token == "5"

