"""
Tests for NodeService.
"""

import pytest

from app.repository.errors import NotFoundError


@pytest.mark.asyncio
async def test_create_node(node_service, nodetype_service):
    """Test creating a node."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    
    data = '{"title": "Hello World", "content": "My first article"}'
    node = await node_service.create(node_type.id, data)
    
    assert node.id is not None
    assert node.node_type_id == node_type.id
    assert node.data == data


@pytest.mark.asyncio
async def test_create_node_missing_node_type_id(node_service):
    """Test creating a node without node_type_id raises ValueError."""
    with pytest.raises(ValueError, match="node_type_id is required"):
        await node_service.create("", '{}')


@pytest.mark.asyncio
async def test_create_node_invalid_node_type(node_service):
    """Test creating a node with invalid node_type_id raises NotFoundError."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    with pytest.raises(NotFoundError):
        await node_service.create(non_existent_id, '{}')


@pytest.mark.asyncio
async def test_get_node_by_id(node_service, nodetype_service):
    """Test retrieving a node by ID."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    created = await node_service.create(node_type.id, '{"title": "Test"}')
    
    retrieved = await node_service.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.node_type_id == created.node_type_id


@pytest.mark.asyncio
async def test_update_node(node_service, nodetype_service):
    """Test updating a node."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    created = await node_service.create(node_type.id, '{"title": "Original"}')
    
    updated_data = '{"title": "Updated", "content": "New content"}'
    updated = await node_service.update(created.id, updated_data)
    
    assert updated.data == updated_data


@pytest.mark.asyncio
async def test_delete_node(node_service, nodetype_service):
    """Test deleting a node."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    created = await node_service.create(node_type.id, '{}')
    
    await node_service.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await node_service.get_by_id(created.id)


@pytest.mark.asyncio
async def test_list_nodes(node_service, nodetype_service):
    """Test listing nodes with pagination."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    
    # Create multiple nodes
    for i in range(5):
        data = f'{{"title": "Article {i}"}}'
        await node_service.create(node_type.id, data)
    
    nodes, result = await node_service.list(None, page_size=10, page_token="")
    
    assert len(nodes) == 5
    assert result.total_count == 5


@pytest.mark.asyncio
async def test_list_nodes_filtered_by_type(node_service, nodetype_service):
    """Test listing nodes filtered by node type."""
    node_type1 = await nodetype_service.create("Article", "Blog article", '{}')
    node_type2 = await nodetype_service.create("Comment", "Comment", '{}')
    
    # Create nodes of different types
    for i in range(3):
        await node_service.create(node_type1.id, '{}')
    
    for i in range(2):
        await node_service.create(node_type2.id, '{}')
    
    # List nodes of type 1
    nodes, result = await node_service.list(node_type1.id, page_size=10, page_token="")
    
    assert len(nodes) == 3
    assert all(n.node_type_id == node_type1.id for n in nodes)

