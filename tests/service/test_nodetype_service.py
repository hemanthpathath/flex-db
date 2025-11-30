"""
Tests for NodeTypeService.
"""

import pytest

from app.repository.errors import NotFoundError


@pytest.mark.asyncio
async def test_create_node_type(nodetype_service):
    """Test creating a node type."""
    schema = '{"title": "string", "content": "string"}'
    node_type = await nodetype_service.create("Article", "Blog article", schema)
    
    assert node_type.id is not None
    assert node_type.name == "Article"
    assert node_type.description == "Blog article"
    assert node_type.schema == schema


@pytest.mark.asyncio
async def test_create_node_type_missing_name(nodetype_service):
    """Test creating a node type without name raises ValueError."""
    with pytest.raises(ValueError, match="name is required"):
        await nodetype_service.create("", "Description", '{}')


@pytest.mark.asyncio
async def test_get_node_type_by_id(nodetype_service):
    """Test retrieving a node type by ID."""
    created = await nodetype_service.create("Article", "Blog article", '{}')
    
    retrieved = await nodetype_service.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.name == created.name


@pytest.mark.asyncio
async def test_update_node_type(nodetype_service):
    """Test updating a node type."""
    created = await nodetype_service.create("Article", "Blog article", '{}')
    
    updated = await nodetype_service.update(
        created.id,
        name="Updated Article",
        description="Updated description",
        schema='{"title": "string", "author": "string"}'
    )
    
    assert updated.name == "Updated Article"
    assert updated.description == "Updated description"
    assert updated.schema == '{"title": "string", "author": "string"}'


@pytest.mark.asyncio
async def test_update_node_type_partial(nodetype_service):
    """Test updating a node type with partial fields."""
    schema = '{"title": "string"}'
    created = await nodetype_service.create("Article", "Blog article", schema)
    
    updated = await nodetype_service.update(
        created.id,
        name="",
        description="Updated description only",
        schema=""
    )
    
    assert updated.name == "Article"  # Unchanged
    assert updated.description == "Updated description only"
    assert updated.schema == schema  # Unchanged


@pytest.mark.asyncio
async def test_delete_node_type(nodetype_service):
    """Test deleting a node type."""
    created = await nodetype_service.create("Article", "Blog article", '{}')
    
    await nodetype_service.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await nodetype_service.get_by_id(created.id)


@pytest.mark.asyncio
async def test_list_node_types(nodetype_service):
    """Test listing node types with pagination."""
    # Create multiple node types
    for i in range(5):
        await nodetype_service.create(f"Type {i}", f"Description {i}", '{}')
    
    node_types, result = await nodetype_service.list(page_size=10, page_token="")
    
    assert len(node_types) == 5
    assert result.total_count == 5

