# Test Organization Patterns

This document explains the test organization pattern used in this project and compares it with alternative approaches.

## Current Structure (Mirror Pattern)

Our tests mirror the source code structure in a separate `tests/` directory:

```
app/
├── repository/
│   ├── tenant_repo.py          → tests/repository/test_tenant_repo.py
│   └── user_repo.py            → tests/repository/test_user_repo.py
├── service/
│   ├── tenant_service.py       → tests/service/test_tenant_service.py
│   └── user_service.py         → tests/service/test_user_service.py
└── jsonrpc/
    └── handlers.py             → tests/jsonrpc/test_handlers.py
```

**Advantages:**
- ✅ Clear relationship between source and test files
- ✅ Easy to locate tests for any component
- ✅ Clean separation of source and test code
- ✅ Tests don't clutter the source directories
- ✅ Easy to exclude tests from deployment packages
- ✅ Centralized test configuration and fixtures

## Alternative Patterns

### 1. Adjacent Test Files

Some projects place test files next to source files:

```
app/
├── repository/
│   ├── tenant_repo.py
│   ├── test_tenant_repo.py     ← Test next to source
│   └── user_repo.py
```

**Pros:**
- Very clear which tests belong to which file
- Easy to find tests while browsing source

**Cons:**
- Clutters source directories
- Requires careful .gitignore patterns
- Tests shipped with source code (unless excluded)
- Harder to run all tests at once

### 2. Full Path Mirroring

Some projects mirror the exact path including the `app/` prefix:

```
tests/
└── app/
    ├── repository/
    │   └── test_tenant_repo.py
    └── service/
        └── test_tenant_service.py
```

**Pros:**
- Exact 1:1 mapping with source structure
- Can use same imports as source

**Cons:**
- More nested directories
- The `app/` prefix in tests is redundant

### 3. Flat Tests Directory

All tests in one flat directory:

```
tests/
├── test_tenant_repo.py
├── test_user_repo.py
├── test_tenant_service.py
└── test_user_service.py
```

**Pros:**
- Simple structure
- Easy to see all tests

**Cons:**
- Hard to navigate with many tests
- No clear organization
- Harder to find related tests

## Why We Chose the Mirror Pattern

We use the **mirror pattern** (our current structure) because:

1. **Scalability**: Works well as the project grows
2. **Clarity**: Easy to find tests for any component
3. **Separation**: Clean separation of concerns
4. **Industry Standard**: Widely used in Python projects (Django, Flask, FastAPI examples)
5. **Tooling**: Works well with pytest's discovery mechanisms

## Test File Naming Convention

We follow the convention:
- Source file: `tenant_repo.py`
- Test file: `test_tenant_repo.py`

This makes it immediately clear:
- What is being tested (`tenant_repo`)
- That it's a test file (`test_` prefix)

## Running Tests

The mirror structure works seamlessly with pytest:

```bash
# Run tests for a specific module
pytest tests/repository/test_tenant_repo.py

# Run all repository tests
pytest tests/repository/

# Run all tests
pytest tests/
```

## References

This pattern is commonly used in:
- Django projects (tests/ directory mirroring app structure)
- Flask projects (tests/ directory)
- FastAPI examples
- Most Python web frameworks

It's also recommended in:
- The Hitchhiker's Guide to Python
- Python Packaging User Guide
- pytest documentation

