# Test Suite for flex-db

This directory contains comprehensive tests for the flex-db backend.

## Test Structure

The test directory structure mirrors the source code organization, making it easy to locate tests for specific components:

```
tests/
├── __init__.py
├── conftest.py                    # Shared pytest fixtures
├── repository/                    # Repository layer tests
│   ├── __init__.py
│   ├── test_tenant_repo.py       # Tests for TenantRepository
│   ├── test_user_repo.py         # Tests for UserRepository
│   ├── test_nodetype_repo.py     # Tests for NodeTypeRepository
│   ├── test_node_repo.py         # Tests for NodeRepository
│   └── test_relationship_repo.py # Tests for RelationshipRepository
├── service/                       # Service layer tests
│   ├── __init__.py
│   ├── test_tenant_service.py    # Tests for TenantService
│   ├── test_user_service.py      # Tests for UserService
│   ├── test_nodetype_service.py  # Tests for NodeTypeService
│   ├── test_node_service.py      # Tests for NodeService
│   └── test_relationship_service.py # Tests for RelationshipService
├── jsonrpc/                       # JSON-RPC layer tests
│   ├── __init__.py
│   └── test_handlers.py          # Tests for JSON-RPC handlers
└── api/                           # API integration tests
    ├── __init__.py
    └── test_integration.py       # End-to-end API workflow tests
```

This structure mirrors the source code organization:
- `app/repository/tenant_repo.py` → `tests/repository/test_tenant_repo.py`
- `app/service/tenant_service.py` → `tests/service/test_tenant_service.py`
- `app/jsonrpc/handlers.py` → `tests/jsonrpc/test_handlers.py`

## Test Coverage

### Repository Layer Tests (`tests/repository/`)
- `test_tenant_repo.py` - TenantRepository CRUD operations, pagination
- `test_user_repo.py` - UserRepository CRUD and tenant membership
- `test_nodetype_repo.py` - NodeTypeRepository operations
- `test_node_repo.py` - NodeRepository operations with filtering
- `test_relationship_repo.py` - RelationshipRepository operations

### Service Layer Tests (`tests/service/`)
- `test_tenant_service.py` - TenantService business logic and validation
- `test_user_service.py` - UserService operations
- `test_nodetype_service.py` - NodeTypeService operations
- `test_node_service.py` - NodeService with validation
- `test_relationship_service.py` - RelationshipService operations

### API Tests
- `tests/jsonrpc/test_handlers.py` - JSON-RPC method handler tests
- `tests/api/test_integration.py` - End-to-end API workflow tests

## Running Tests

### Prerequisites

1. **PostgreSQL Database**: You need a PostgreSQL database running. The tests use a separate test database (`dbaas_control_test`).

2. **Environment Variables**: Set these environment variables if needed (defaults shown):
   ```bash
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_USER=postgres
   export DB_PASSWORD=postgres
   ```

### Run All Tests

```bash
# Install dependencies first
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/repository/test_tenant_repo.py

# Run specific test
pytest tests/repository/test_tenant_repo.py::test_create_tenant
```

### Run Tests by Category

```bash
# Run repository tests only
pytest tests/repository/

# Run service tests only
pytest tests/service/

# Run JSON-RPC tests only
pytest tests/jsonrpc/

# Run API integration tests only
pytest tests/api/
```

### Run Tests in Docker

If you have Docker Compose set up, you can run tests in isolation:

```bash
make test-all
```

This uses the test profile in `docker-compose.yml` which sets up a clean test database.

## Test Fixtures

The test suite uses pytest fixtures for setup and teardown:

- `test_config` - Test database configuration
- `control_db` - Control database connection (session-scoped)
- `clean_control_db` - Clean control database (function-scoped, cleaned before each test)
- `tenant_db_manager` - Tenant database manager instance
- `tenant_repo`, `user_repo`, etc. - Repository instances
- `tenant_service`, `user_service`, etc. - Service instances
- `tenant_db` - Tenant database connection (with test tenant created)
- `test_tenant`, `test_user`, etc. - Pre-created test entities
- `async_client` - HTTP client for API testing

## Test Database

Tests use a separate test database to avoid interfering with development data:

- Control database: `dbaas_control_test`
- Tenant databases: `dbaas_tenant_test_*`

The test database is cleaned automatically before each test function to ensure test isolation.

## Writing New Tests

When adding new tests:

1. **Use existing fixtures** when possible to avoid duplication
2. **Follow naming conventions**: `test_<functionality>_<scenario>`
3. **Test both success and error cases**
4. **Use appropriate pytest markers** (e.g., `@pytest.mark.asyncio` for async tests)
5. **Clean up test data** - fixtures handle this automatically, but be aware of test isolation

### Example Test

```python
# tests/service/test_tenant_service.py
@pytest.mark.asyncio
async def test_create_tenant(tenant_service):
    """Test creating a tenant."""
    tenant = await tenant_service.create("test-tenant", "Test Tenant")
    
    assert tenant.id is not None
    assert tenant.slug == "test-tenant"
    assert tenant.name == "Test Tenant"
```

**Note**: The test file name should match the source file being tested:
- Source: `app/service/tenant_service.py`
- Test: `tests/service/test_tenant_service.py`

## Continuous Integration

The test suite is designed to be run in CI/CD pipelines. Ensure:

1. PostgreSQL is available in the CI environment
2. Database connection environment variables are set
3. Tests run in isolation (separate test database)

## Troubleshooting

### Tests fail with database connection errors

- Ensure PostgreSQL is running
- Check environment variables match your database setup
- Verify the test database doesn't exist (it will be created automatically)

### Tests interfere with each other

- Each test should be isolated (fixtures handle cleanup)
- If issues persist, check that fixtures are properly scoped

### Async test warnings

- Ensure `pytest-asyncio` is installed
- Check that `asyncio_mode = auto` is set in `pytest.ini`

