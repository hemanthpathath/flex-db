"""
Pytest configuration and fixtures for flex-db tests.
"""

import asyncio
import os
import uuid
from typing import AsyncGenerator, Generator

import asyncpg
import pytest
from httpx import AsyncClient

from app.config import Config, default_config
from app.db import Database, connect_control_db, run_control_migrations, ensure_control_database_exists
from app.db.tenant_db_manager import TenantDatabaseManager
from app.repository import (
    TenantRepository,
    UserRepository,
    NodeTypeRepository,
    NodeRepository,
    RelationshipRepository,
)
from app.service import (
    TenantService,
    UserService,
    NodeTypeService,
    NodeService,
    RelationshipService,
)
from main import create_app


# Test database configuration
TEST_CONTROL_DB_NAME = "dbaas_control_test"
TEST_TENANT_DB_PREFIX = "dbaas_tenant_test_"


@pytest.fixture(scope="session")
def test_config() -> Config:
    """Create test configuration."""
    return Config(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        control_db_name=TEST_CONTROL_DB_NAME,
        tenant_db_prefix=TEST_TENANT_DB_PREFIX,
        db_name=TEST_CONTROL_DB_NAME,
        ssl_mode="disable",
    )


@pytest.fixture(scope="session", autouse=True)
def _setup_test_db(test_config: Config):
    """Session-scoped setup: ensure database exists and run migrations.
    
    Runs once per test session to set up the database schema.
    This is a synchronous fixture to avoid event loop conflicts.
    """
    import asyncio
    
    async def _setup():
        # Ensure control database exists
        await ensure_control_database_exists(test_config)
        
        # Connect and run migrations once per test session
        db = await connect_control_db(test_config)
        try:
            await run_control_migrations(db)
        finally:
            await db.close()
    
    # Run setup in a fresh event loop
    asyncio.run(_setup())


@pytest.fixture(scope="function")
async def clean_control_db(test_config: Config) -> AsyncGenerator[Database, None]:
    """Provide a clean control database for each test.
    
    Creates a fresh connection pool in the current event loop to avoid loop mismatch issues.
    """
    # Create a fresh connection pool in the current event loop
    db = await connect_control_db(test_config)
    
    # Clean up all tables before test
    async with db.pool.acquire() as conn:
        # Disable foreign key checks temporarily
        await conn.execute("SET session_replication_role = 'replica';")
        
        # Delete all data (in reverse order of dependencies)
        await conn.execute("DELETE FROM tenant_users")
        await conn.execute("DELETE FROM tenant_migrations")
        await conn.execute("DELETE FROM tenant_databases")
        await conn.execute("DELETE FROM users")
        await conn.execute("DELETE FROM tenants")
        
        # Re-enable foreign key checks
        await conn.execute("SET session_replication_role = 'origin';")
    
    yield db
    
    # Cleanup: close connection pool
    await db.close()


@pytest.fixture
async def tenant_db_manager(test_config: Config, clean_control_db: Database) -> TenantDatabaseManager:
    """Create tenant database manager."""
    return TenantDatabaseManager(test_config, clean_control_db)


@pytest.fixture
async def tenant_repo(clean_control_db: Database) -> TenantRepository:
    """Create tenant repository."""
    return TenantRepository(clean_control_db)


@pytest.fixture
async def user_repo(clean_control_db: Database) -> UserRepository:
    """Create user repository."""
    return UserRepository(clean_control_db)


@pytest.fixture
async def tenant_service(tenant_repo: TenantRepository, tenant_db_manager: TenantDatabaseManager) -> TenantService:
    """Create tenant service."""
    return TenantService(tenant_repo, tenant_db_manager)


@pytest.fixture
async def user_service(user_repo: UserRepository) -> UserService:
    """Create user service."""
    return UserService(user_repo)


@pytest.fixture
async def tenant_db(
    test_config: Config,
    tenant_service: TenantService,
    tenant_db_manager: TenantDatabaseManager,
    clean_control_db: Database
) -> AsyncGenerator[Database, None]:
    """Create a test tenant and return its database connection."""
    import uuid
    
    # Create a unique tenant slug for each test to avoid database reuse
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    tenant = await tenant_service.create(unique_slug, "Test Tenant")
    
    # Get tenant database
    tenant_db = await tenant_db_manager.get_tenant_db(tenant.id)
    
    yield tenant_db
    
    # Cleanup tenant database after test
    async with tenant_db.pool.acquire() as conn:
        await conn.execute("SET session_replication_role = 'replica';")
        await conn.execute("DELETE FROM relationships")
        await conn.execute("DELETE FROM nodes")
        await conn.execute("DELETE FROM node_types")
        await conn.execute("DELETE FROM schema_migrations")  # Clean migrations table too
        await conn.execute("SET session_replication_role = 'origin';")
    
    # Clean tenant migration tracking from control DB
    async with clean_control_db.pool.acquire() as conn:
        await conn.execute("DELETE FROM tenant_migrations WHERE tenant_id = $1", tenant.id)
        await conn.execute("DELETE FROM tenant_databases WHERE tenant_id = $1", tenant.id)


@pytest.fixture
async def nodetype_repo(tenant_db: Database) -> NodeTypeRepository:
    """Create node type repository for tenant database."""
    return NodeTypeRepository(tenant_db)


@pytest.fixture
async def node_repo(tenant_db: Database) -> NodeRepository:
    """Create node repository for tenant database."""
    return NodeRepository(tenant_db)


@pytest.fixture
async def relationship_repo(tenant_db: Database) -> RelationshipRepository:
    """Create relationship repository for tenant database."""
    return RelationshipRepository(tenant_db)


@pytest.fixture
async def nodetype_service(nodetype_repo: NodeTypeRepository) -> NodeTypeService:
    """Create node type service."""
    return NodeTypeService(nodetype_repo)


@pytest.fixture
async def node_service(node_repo: NodeRepository, nodetype_repo: NodeTypeRepository) -> NodeService:
    """Create node service."""
    return NodeService(node_repo, nodetype_repo)


@pytest.fixture
async def relationship_service(relationship_repo: RelationshipRepository, node_repo: NodeRepository) -> RelationshipService:
    """Create relationship service."""
    return RelationshipService(relationship_repo, node_repo)


@pytest.fixture
async def test_tenant(tenant_service: TenantService) -> dict:
    """Create and return a test tenant."""
    import uuid
    unique_slug = f"test-tenant-{uuid.uuid4().hex[:8]}"
    tenant = await tenant_service.create(unique_slug, "Test Tenant")
    return tenant.to_dict()


@pytest.fixture
async def test_user(user_service: UserService) -> dict:
    """Create and return a test user."""
    user = await user_service.create("test@example.com", "Test User")
    return user.to_dict()


@pytest.fixture
async def test_node_type(nodetype_service: NodeTypeService) -> dict:
    """Create and return a test node type."""
    schema = '{"title": "string", "content": "string"}'
    node_type = await nodetype_service.create("Article", "Blog article", schema)
    return node_type.to_dict()


@pytest.fixture
async def test_node(node_service: NodeService, test_node_type: dict) -> dict:
    """Create and return a test node."""
    data = '{"title": "Hello World", "content": "My first article"}'
    node = await node_service.create(test_node_type["id"], data)
    return node.to_dict()


@pytest.fixture
async def test_relationship(
    relationship_service: RelationshipService,
    test_node: dict,
    node_service: NodeService,
    test_node_type: dict
) -> dict:
    """Create and return a test relationship."""
    # Create second node
    data = '{"title": "Second Article", "content": "Another article"}'
    second_node = await node_service.create(test_node_type["id"], data)
    
    # Create relationship
    rel_data = '{"note": "reference"}'
    rel = await relationship_service.create(
        test_node["id"],
        second_node.id,
        "references",
        rel_data
    )
    return rel.to_dict()


@pytest.fixture
async def async_client(
    tenant_service: TenantService,
    user_service: UserService,
    tenant_db_manager: TenantDatabaseManager
) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing FastAPI app."""
    from fastapi import FastAPI
    from app.api.dependencies import set_tenant_db_manager
    from app.jsonrpc.handlers import register_methods
    from app.jsonrpc.server import router as jsonrpc_router
    
    # Initialize app dependencies before creating app
    set_tenant_db_manager(tenant_db_manager)
    register_methods(tenant_service, user_service)
    
    # Create minimal app for testing (without lifespan to avoid database setup)
    app = FastAPI(
        title="flex-db API Test",
        description="Test API",
        version="1.0.0",
    )
    app.include_router(jsonrpc_router)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}
    
    @app.get("/openrpc.json")
    async def get_openrpc_spec():
        """Get OpenRPC specification."""
        from app.jsonrpc.openrpc import get_openrpc_spec_json
        from fastapi import Response
        spec_json = get_openrpc_spec_json()
        return Response(content=spec_json, media_type="application/json")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

