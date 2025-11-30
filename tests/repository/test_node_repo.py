"""
Tests for NodeRepository.
"""

import pytest

from app.repository.errors import NotFoundError
from app.repository.models import Node, NodeType, ListOptions


@pytest.mark.asyncio
async def test_create_node(node_repo, nodetype_repo):
    """Test creating a node."""
    # Create node type first
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    data = '{"title": "Hello World", "content": "My first article"}'
    node = Node(node_type_id=node_type.id, data=data)
    created = await node_repo.create(node)
    
    assert created.id is not None
    assert created.node_type_id == node_type.id
    assert created.data == data
    assert created.created_at is not None
    assert created.updated_at is not None


@pytest.mark.asyncio
async def test_create_node_empty_data(node_repo, nodetype_repo):
    """Test creating a node with empty data."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    node = Node(node_type_id=node_type.id, data="")
    created = await node_repo.create(node)
    
    assert created.data == "{}"  # Defaults to empty JSON object


@pytest.mark.asyncio
async def test_get_node_by_id(node_repo, nodetype_repo):
    """Test retrieving a node by ID."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    data = '{"title": "Hello World"}'
    node = Node(node_type_id=node_type.id, data=data)
    created = await node_repo.create(node)
    
    retrieved = await node_repo.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.node_type_id == created.node_type_id
    assert retrieved.data == created.data


@pytest.mark.asyncio
async def test_get_node_not_found(node_repo):
    """Test retrieving a non-existent node raises NotFoundError."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    with pytest.raises(NotFoundError):
        await node_repo.get_by_id(non_existent_id)


@pytest.mark.asyncio
async def test_update_node(node_repo, nodetype_repo):
    """Test updating a node."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    data = '{"title": "Hello World"}'
    node = Node(node_type_id=node_type.id, data=data)
    created = await node_repo.create(node)
    
    created.data = '{"title": "Updated Title", "content": "New content"}'
    updated = await node_repo.update(created)
    
    assert updated.data == '{"title": "Updated Title", "content": "New content"}'
    # Compare as timestamps to avoid timezone issues
    assert updated.updated_at.timestamp() >= created.updated_at.timestamp()


@pytest.mark.asyncio
async def test_delete_node(node_repo, nodetype_repo):
    """Test deleting a node."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    node = Node(node_type_id=node_type.id, data='{}')
    created = await node_repo.create(node)
    
    await node_repo.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await node_repo.get_by_id(created.id)


@pytest.mark.asyncio
async def test_list_nodes(node_repo, nodetype_repo):
    """Test listing nodes with pagination."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    # Create multiple nodes
    for i in range(5):
        data = f'{{"title": "Article {i}"}}'
        node = Node(node_type_id=node_type.id, data=data)
        await node_repo.create(node)
    
    nodes, result = await node_repo.list(None, ListOptions(page_size=10, page_token=""))
    
    assert len(nodes) == 5
    assert result.total_count == 5


@pytest.mark.asyncio
async def test_list_nodes_filtered_by_type(node_repo, nodetype_repo):
    """Test listing nodes filtered by node type."""
    node_type1 = NodeType(name="Article", schema='{}')
    node_type1 = await nodetype_repo.create(node_type1)
    
    node_type2 = NodeType(name="Comment", schema='{}')
    node_type2 = await nodetype_repo.create(node_type2)
    
    # Create nodes of different types
    for i in range(3):
        node = Node(node_type_id=node_type1.id, data='{}')
        await node_repo.create(node)
    
    for i in range(2):
        node = Node(node_type_id=node_type2.id, data='{}')
        await node_repo.create(node)
    
    # List nodes of type 1
    nodes, result = await node_repo.list(node_type1.id, ListOptions(page_size=10, page_token=""))
    
    assert len(nodes) == 3
    assert all(n.node_type_id == node_type1.id for n in nodes)

