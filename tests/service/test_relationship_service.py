"""
Tests for RelationshipService.
"""

import pytest

from app.repository.errors import NotFoundError


@pytest.mark.asyncio
async def test_create_relationship(relationship_service, node_service, nodetype_service):
    """Test creating a relationship."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    
    source_node = await node_service.create(node_type.id, '{}')
    target_node = await node_service.create(node_type.id, '{}')
    
    rel_data = '{"note": "reference"}'
    rel = await relationship_service.create(
        source_node.id,
        target_node.id,
        "references",
        rel_data
    )
    
    assert rel.id is not None
    assert rel.source_node_id == source_node.id
    assert rel.target_node_id == target_node.id
    assert rel.relationship_type == "references"
    assert rel.data == rel_data


@pytest.mark.asyncio
async def test_create_relationship_missing_source(relationship_service):
    """Test creating a relationship without source_node_id raises ValueError."""
    with pytest.raises(ValueError, match="source_node_id is required"):
        await relationship_service.create("", "target-id", "references", '{}')


@pytest.mark.asyncio
async def test_create_relationship_missing_target(relationship_service):
    """Test creating a relationship without target_node_id raises ValueError."""
    with pytest.raises(ValueError, match="target_node_id is required"):
        await relationship_service.create("source-id", "", "references", '{}')


@pytest.mark.asyncio
async def test_create_relationship_missing_type(relationship_service, node_service, nodetype_service):
    """Test creating a relationship without relationship_type raises ValueError."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    source_node = await node_service.create(node_type.id, '{}')
    target_node = await node_service.create(node_type.id, '{}')
    
    with pytest.raises(ValueError, match="relationship_type is required"):
        await relationship_service.create(source_node.id, target_node.id, "", '{}')


@pytest.mark.asyncio
async def test_create_relationship_invalid_source(relationship_service, node_service, nodetype_service):
    """Test creating a relationship with invalid source_node_id raises NotFoundError."""
    import uuid
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    target_node = await node_service.create(node_type.id, '{}')
    non_existent_id = str(uuid.uuid4())
    
    with pytest.raises(NotFoundError):
        await relationship_service.create(non_existent_id, target_node.id, "references", '{}')


@pytest.mark.asyncio
async def test_get_relationship_by_id(relationship_service, node_service, nodetype_service):
    """Test retrieving a relationship by ID."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    source_node = await node_service.create(node_type.id, '{}')
    target_node = await node_service.create(node_type.id, '{}')
    
    created = await relationship_service.create(source_node.id, target_node.id, "references", '{}')
    
    retrieved = await relationship_service.get_by_id(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.source_node_id == created.source_node_id
    assert retrieved.target_node_id == created.target_node_id


@pytest.mark.asyncio
async def test_update_relationship(relationship_service, node_service, nodetype_service):
    """Test updating a relationship."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    source_node = await node_service.create(node_type.id, '{}')
    target_node = await node_service.create(node_type.id, '{}')
    
    created = await relationship_service.create(source_node.id, target_node.id, "references", '{}')
    
    updated = await relationship_service.update(
        created.id,
        rel_type="links_to",
        data='{"note": "updated"}'
    )
    
    assert updated.relationship_type == "links_to"
    assert updated.data == '{"note": "updated"}'


@pytest.mark.asyncio
async def test_delete_relationship(relationship_service, node_service, nodetype_service):
    """Test deleting a relationship."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    source_node = await node_service.create(node_type.id, '{}')
    target_node = await node_service.create(node_type.id, '{}')
    
    created = await relationship_service.create(source_node.id, target_node.id, "references", '{}')
    
    await relationship_service.delete(created.id)
    
    with pytest.raises(NotFoundError):
        await relationship_service.get_by_id(created.id)


@pytest.mark.asyncio
async def test_list_relationships(relationship_service, node_service, nodetype_service):
    """Test listing relationships with pagination."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    source_node = await node_service.create(node_type.id, '{}')
    
    # Create multiple relationships
    for i in range(3):
        target_node = await node_service.create(node_type.id, '{}')
        await relationship_service.create(source_node.id, target_node.id, "references", '{}')
    
    rels, result = await relationship_service.list(None, None, None, page_size=10, page_token="")
    
    assert len(rels) == 3
    assert result.total_count == 3


@pytest.mark.asyncio
async def test_list_relationships_filtered(relationship_service, node_service, nodetype_service):
    """Test listing relationships with filters."""
    node_type = await nodetype_service.create("Article", "Blog article", '{}')
    source_node = await node_service.create(node_type.id, '{}')
    target_node = await node_service.create(node_type.id, '{}')
    
    # Create relationships with different types
    await relationship_service.create(source_node.id, target_node.id, "references", '{}')
    await relationship_service.create(source_node.id, target_node.id, "links_to", '{}')
    
    # Filter by source node
    rels, _ = await relationship_service.list(
        source_node.id, None, None, page_size=10, page_token=""
    )
    assert len(rels) == 2
    
    # Filter by relationship type
    rels, _ = await relationship_service.list(
        None, None, "references", page_size=10, page_token=""
    )
    assert len(rels) == 1
    assert rels[0].relationship_type == "references"

