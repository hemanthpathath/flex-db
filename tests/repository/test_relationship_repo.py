"""
Tests for RelationshipRepository.
"""

import pytest

from app.repository.errors import NotFoundError
from app.repository.models import Relationship, Node, NodeType, ListOptions


@pytest.mark.asyncio
async def test_create_relationship(relationship_repo, node_repo, nodetype_repo):
    """Test creating a relationship."""
    # Create node type
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    # Create source and target nodes
    source_node = Node(node_type_id=node_type.id, data='{}')
    source_node = await node_repo.create(source_node)
    
    target_node = Node(node_type_id=node_type.id, data='{}')
    target_node = await node_repo.create(target_node)
    
    # Create relationship
    rel_data = '{"note": "reference"}'
    rel = Relationship(
        source_node_id=source_node.id,
        target_node_id=target_node.id,
        relationship_type="references",
        data=rel_data
    )
    created = await relationship_repo.create(rel)
    
    assert created.id is not None
    assert created.source_node_id == source_node.id
    assert created.target_node_id == target_node.id
    assert created.relationship_type == "references"
    assert created.data == rel_data
    assert created.created_at is not None
    assert created.updated_at is not None


@pytest.mark.asyncio
async def test_get_relationship_by_id(relationship_repo, node_repo, nodetype_repo):
    """Test retrieving a relationship by ID."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    source_node = Node(node_type_id=node_type.id, data='{}')
    source_node = await node_repo.create(source_node)
    
    target_node = Node(node_type_id=node_type.id, data='{}')
    target_node = await node_repo.create(target_node)
    
    rel = Relationship(
        source_node_id=source_node.id,
        target_node_id=target_node.id,
        relationship_type="references",
        data='{}'
    )
    created = await relationship_repo.create(rel)
    
    retrieved = await relationship_repo.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.source_node_id == created.source_node_id
    assert retrieved.target_node_id == created.target_node_id
    assert retrieved.relationship_type == created.relationship_type


@pytest.mark.asyncio
async def test_get_relationship_not_found(relationship_repo):
    """Test retrieving a non-existent relationship raises NotFoundError."""
    import uuid
    non_existent_id = str(uuid.uuid4())
    with pytest.raises(NotFoundError):
        await relationship_repo.get_by_id(non_existent_id)


@pytest.mark.asyncio
async def test_update_relationship(relationship_repo, node_repo, nodetype_repo):
    """Test updating a relationship."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    source_node = Node(node_type_id=node_type.id, data='{}')
    source_node = await node_repo.create(source_node)
    
    target_node = Node(node_type_id=node_type.id, data='{}')
    target_node = await node_repo.create(target_node)
    
    rel = Relationship(
        source_node_id=source_node.id,
        target_node_id=target_node.id,
        relationship_type="references",
        data='{}'
    )
    created = await relationship_repo.create(rel)
    
    created.relationship_type = "links_to"
    created.data = '{"note": "updated"}'
    updated = await relationship_repo.update(created)
    
    assert updated.relationship_type == "links_to"
    assert updated.data == '{"note": "updated"}'
    # Compare as timestamps to avoid timezone issues
    assert updated.updated_at.timestamp() >= created.updated_at.timestamp()


@pytest.mark.asyncio
async def test_delete_relationship(relationship_repo, node_repo, nodetype_repo):
    """Test deleting a relationship."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    source_node = Node(node_type_id=node_type.id, data='{}')
    source_node = await node_repo.create(source_node)
    
    target_node = Node(node_type_id=node_type.id, data='{}')
    target_node = await node_repo.create(target_node)
    
    rel = Relationship(
        source_node_id=source_node.id,
        target_node_id=target_node.id,
        relationship_type="references",
        data='{}'
    )
    created = await relationship_repo.create(rel)
    
    await relationship_repo.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await relationship_repo.get_by_id(created.id)


@pytest.mark.asyncio
async def test_list_relationships(relationship_repo, node_repo, nodetype_repo):
    """Test listing relationships with pagination."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    source_node = Node(node_type_id=node_type.id, data='{}')
    source_node = await node_repo.create(source_node)
    
    # Create multiple relationships
    for i in range(3):
        target_node = Node(node_type_id=node_type.id, data='{}')
        target_node = await node_repo.create(target_node)
        
        rel = Relationship(
            source_node_id=source_node.id,
            target_node_id=target_node.id,
            relationship_type="references",
            data='{}'
        )
        await relationship_repo.create(rel)
    
    rels, result = await relationship_repo.list(None, None, None, ListOptions(page_size=10, page_token=""))
    
    assert len(rels) == 3
    assert result.total_count == 3


@pytest.mark.asyncio
async def test_list_relationships_filtered(relationship_repo, node_repo, nodetype_repo):
    """Test listing relationships with filters."""
    node_type = NodeType(name="Article", schema='{}')
    node_type = await nodetype_repo.create(node_type)
    
    source_node = Node(node_type_id=node_type.id, data='{}')
    source_node = await node_repo.create(source_node)
    
    target_node = Node(node_type_id=node_type.id, data='{}')
    target_node = await node_repo.create(target_node)
    
    # Create relationships with different types
    rel1 = Relationship(
        source_node_id=source_node.id,
        target_node_id=target_node.id,
        relationship_type="references",
        data='{}'
    )
    await relationship_repo.create(rel1)
    
    rel2 = Relationship(
        source_node_id=source_node.id,
        target_node_id=target_node.id,
        relationship_type="links_to",
        data='{}'
    )
    await relationship_repo.create(rel2)
    
    # Filter by source node
    rels, _ = await relationship_repo.list(
        source_node.id, None, None, ListOptions(page_size=10, page_token="")
    )
    assert len(rels) == 2
    
    # Filter by relationship type
    rels, _ = await relationship_repo.list(
        None, None, "references", ListOptions(page_size=10, page_token="")
    )
    assert len(rels) == 1
    assert rels[0].relationship_type == "references"

