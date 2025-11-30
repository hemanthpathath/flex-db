# Docker-Based Test Execution

This document explains how tests are run in isolated Docker containers.

## Quick Start

Run all tests in isolation:

```bash
make test-all
```

This command:
1. Builds the test environment
2. Starts an isolated PostgreSQL test database
3. Runs all tests in a dedicated container
4. Tears down everything after tests complete
5. Returns the appropriate exit code

## Test Isolation Architecture

### Components

1. **postgres-test** - Isolated PostgreSQL database
   - Uses `tmpfs` (in-memory filesystem) for maximum performance
   - No data persistence - completely fresh for each test run
   - Separate from development database
   - Database name: `dbaas_control_test`
   - Tenant prefix: `dbaas_tenant_test_`

2. **test-runner** - Container that executes tests
   - Runs `pytest` against all tests
   - Connects to `postgres-test` database
   - Mounts source code and tests as read-only volumes
   - Exits with test result code

3. **flex-db-test** (optional) - Test backend service
   - Currently not required for tests (tests use fixture-based FastAPI apps)
   - Available for future end-to-end API tests if needed

### Isolation Features

✅ **Separate Database**: Test database completely isolated from development  
✅ **No Persistence**: tmpfs means no leftover data between runs  
✅ **Read-Only Volumes**: Tests run against committed code, not local changes  
✅ **Automatic Cleanup**: All containers removed after tests  
✅ **Fresh State**: Each test run starts with a clean database  

## Test Execution Flow

```
┌─────────────────────────────────────────────────┐
│  make test-all                                  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  1. Build Docker images                         │
│     - Builds Python image with dependencies     │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  2. Start test environment                      │
│     - postgres-test (tmpfs database)            │
│     - test-runner (waits for postgres)          │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  3. Wait for PostgreSQL to be ready             │
│     - Health checks                             │
│     - Connection verification                   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  4. Run all tests                               │
│     - pytest tests/ -v --tb=short               │
│     - Repository tests                          │
│     - Service tests                             │
│     - JSON-RPC handler tests                    │
│     - API integration tests                     │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  5. Capture exit code                           │
│     - 0 = all tests passed                      │
│     - non-zero = tests failed                   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  6. Teardown                                    │
│     - Stop all containers                       │
│     - Remove volumes                            │
│     - Clean up                                  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  7. Return exit code                            │
│     - CI/CD can use exit code for pass/fail     │
└─────────────────────────────────────────────────┘
```

## Environment Variables

Test containers use these environment variables:

```bash
DB_HOST=postgres-test              # Test database host
DB_PORT=5432                       # PostgreSQL port
DB_USER=postgres                   # Database user
DB_PASSWORD=postgres               # Database password
DB_CONTROL_NAME=dbaas_control_test # Control database name
DB_TENANT_PREFIX=dbaas_tenant_test_ # Tenant database prefix
DB_NAME=dbaas_test                 # Legacy database name
DB_SSL_MODE=disable                # SSL disabled for local testing
PYTHONPATH=/app                    # Python path
PYTHONDONTWRITEBYTECODE=1          # Don't write .pyc files
PYTHONUNBUFFERED=1                 # Unbuffered output for logs
```

## Manual Test Execution

You can also run tests manually:

```bash
# Start test environment (without running tests)
docker compose --profile test up -d postgres-test

# Run tests manually in the container
docker compose --profile test run --rm test-runner pytest tests/ -v

# View test logs
docker compose --profile test logs -f test-runner

# Clean up
docker compose --profile test down -v
```

## Running Specific Tests

To run specific tests, you can override the command:

```bash
# Run only repository tests
docker compose --profile test run --rm test-runner pytest tests/repository/ -v

# Run only service tests
docker compose --profile test run --rm test-runner pytest tests/service/ -v

# Run a specific test file
docker compose --profile test run --rm test-runner pytest tests/repository/test_tenant_repo.py -v

# Run with coverage
docker compose --profile test run --rm test-runner pytest tests/ --cov=app --cov-report=html -v
```

## Troubleshooting

### Tests fail to connect to database

The test-runner waits up to 30 seconds for PostgreSQL. If it times out:
- Check that postgres-test container is running: `docker compose --profile test ps`
- Check postgres-test logs: `docker compose --profile test logs postgres-test`
- Increase the timeout in the command if needed

### Tests are slow

The tmpfs database should be fast. If tests are slow:
- Check Docker resource limits
- Ensure tmpfs is working: `docker compose --profile test exec postgres-test df -h`
- Consider running tests locally instead

### Tests fail locally but pass in Docker

This usually means:
- Local database state differs from test database
- Local dependencies differ from Docker image
- Environment variables differ

Solution: Always use `make test-all` for consistent results.

### View test output

```bash
# Stream test output in real-time
docker compose --profile test up test-runner

# View logs after tests complete
docker compose --profile test logs test-runner
```

## CI/CD Integration

The `make test-all` command is designed for CI/CD:

```yaml
# Example GitHub Actions
- name: Run tests
  run: make test-all
```

The command:
- Returns exit code 0 on success, non-zero on failure
- Automatically cleans up after tests
- Works consistently across environments

## Benefits of Docker-Based Testing

1. **Consistency**: Same environment for all developers and CI
2. **Isolation**: No conflicts with local development databases
3. **Clean State**: Fresh database for every test run
4. **Reproducibility**: Tests behave the same everywhere
5. **Easy Cleanup**: No manual database cleanup needed
6. **CI/CD Ready**: Works out of the box in CI environments

