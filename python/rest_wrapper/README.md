# flex-db REST Wrapper

A FastAPI-based REST API facade for the flex-db JSON-RPC backend. This wrapper provides a RESTful interface that forwards requests to the existing JSON-RPC backend, offering interactive API documentation via Swagger UI and ReDoc.

## Features

- **REST API**: RESTful endpoints for all JSON-RPC methods
- **OpenAPI Documentation**: Auto-generated OpenAPI 3.1 schema
- **Swagger UI**: Interactive API browser at `/docs`
- **ReDoc**: Alternative API documentation at `/redoc`
- **Pydantic Validation**: Request/response validation using Pydantic models
- **CORS Support**: Cross-Origin Resource Sharing enabled by default
- **Error Mapping**: JSON-RPC errors mapped to appropriate HTTP status codes

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REST API (FastAPI)                       │
│  (Swagger UI, ReDoc, OpenAPI Schema)                        │
├─────────────────────────────────────────────────────────────┤
│                  JSON-RPC Client (httpx)                    │
│  (Request forwarding, Response mapping)                     │
├─────────────────────────────────────────────────────────────┤
│                  JSON-RPC Backend (aiohttp)                 │
│  (Existing backend - unchanged)                             │
├─────────────────────────────────────────────────────────────┤
│                      PostgreSQL                             │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
rest_wrapper/
├── __init__.py
├── main.py              # FastAPI application
├── config.py            # Configuration
├── client.py            # JSON-RPC client
├── models.py            # Pydantic models
├── requirements.txt     # Dependencies
├── routers/
│   ├── __init__.py
│   ├── tenants.py       # Tenant endpoints
│   ├── users.py         # User endpoints
│   ├── node_types.py    # Node type endpoints
│   ├── nodes.py         # Node endpoints
│   └── relationships.py # Relationship endpoints
└── tests/
    ├── __init__.py
    └── test_forwarding.py  # Forwarding tests
```

## Prerequisites

- Python 3.9+
- Running JSON-RPC backend (default: `http://localhost:5000/jsonrpc`)

## Quick Start

### Step 1: Start the JSON-RPC Backend

First, ensure the JSON-RPC backend is running:

```bash
# From the python directory
cd python
./scripts/start.sh
```

Or with Docker:

```bash
docker-compose up -d
```

### Step 2: Install REST Wrapper Dependencies

```bash
# From the python directory
pip install -r rest_wrapper/requirements.txt
```

### Step 3: Run the REST Wrapper

```bash
# From the python directory
PYTHONPATH=. uvicorn rest_wrapper.main:app --host 0.0.0.0 --port 8000
```

Or with hot reload for development:

```bash
PYTHONPATH=. uvicorn rest_wrapper.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Configuration

The REST wrapper can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `JSONRPC_URL` | `http://localhost:5000/jsonrpc` | JSON-RPC backend URL |
| `REST_HOST` | `0.0.0.0` | REST server host |
| `REST_PORT` | `8000` | REST server port |
| `REST_API_TITLE` | `flex-db REST API` | API title in documentation |
| `REST_API_DESCRIPTION` | `REST API facade for flex-db JSON-RPC backend` | API description |
| `REST_API_VERSION` | `1.0.0` | API version |

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Tenants

```bash
# Create a tenant
curl -X POST http://localhost:8000/tenants \
  -H "Content-Type: application/json" \
  -d '{"slug": "acme-corp", "name": "Acme Corporation"}'

# Get a tenant
curl http://localhost:8000/tenants/{tenant_id}

# Update a tenant
curl -X PUT http://localhost:8000/tenants/{tenant_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Delete a tenant
curl -X DELETE http://localhost:8000/tenants/{tenant_id}

# List tenants
curl "http://localhost:8000/tenants?page_size=10"
```

### Users

```bash
# Create a user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "display_name": "John Doe"}'

# Get a user
curl http://localhost:8000/users/{user_id}

# Update a user
curl -X PUT http://localhost:8000/users/{user_id} \
  -H "Content-Type: application/json" \
  -d '{"display_name": "John D."}'

# Delete a user
curl -X DELETE http://localhost:8000/users/{user_id}

# List users
curl http://localhost:8000/users
```

### Tenant Users

```bash
# Add user to tenant
curl -X POST http://localhost:8000/tenants/{tenant_id}/users \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-id", "role": "admin"}'

# Remove user from tenant
curl -X DELETE http://localhost:8000/tenants/{tenant_id}/users/{user_id}

# List tenant users
curl http://localhost:8000/tenants/{tenant_id}/users
```

### Node Types

```bash
# Create a node type
curl -X POST http://localhost:8000/tenants/{tenant_id}/node-types \
  -H "Content-Type: application/json" \
  -d '{"name": "Task", "description": "A task node", "schema": "{}"}'

# Get a node type
curl http://localhost:8000/tenants/{tenant_id}/node-types/{node_type_id}

# Update a node type
curl -X PUT http://localhost:8000/tenants/{tenant_id}/node-types/{node_type_id} \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}'

# Delete a node type
curl -X DELETE http://localhost:8000/tenants/{tenant_id}/node-types/{node_type_id}

# List node types
curl http://localhost:8000/tenants/{tenant_id}/node-types
```

### Nodes

```bash
# Create a node
curl -X POST http://localhost:8000/tenants/{tenant_id}/nodes \
  -H "Content-Type: application/json" \
  -d '{"node_type_id": "node-type-id", "data": "{\"title\": \"My Task\"}"}'

# Get a node
curl http://localhost:8000/tenants/{tenant_id}/nodes/{node_id}

# Update a node
curl -X PUT http://localhost:8000/tenants/{tenant_id}/nodes/{node_id} \
  -H "Content-Type: application/json" \
  -d '{"data": "{\"title\": \"Updated Task\"}"}'

# Delete a node
curl -X DELETE http://localhost:8000/tenants/{tenant_id}/nodes/{node_id}

# List nodes (with optional filter)
curl "http://localhost:8000/tenants/{tenant_id}/nodes?node_type_id=type-id"
```

### Relationships

```bash
# Create a relationship
curl -X POST http://localhost:8000/tenants/{tenant_id}/relationships \
  -H "Content-Type: application/json" \
  -d '{
    "source_node_id": "source-id",
    "target_node_id": "target-id",
    "relationship_type": "depends_on",
    "data": "{}"
  }'

# Get a relationship
curl http://localhost:8000/tenants/{tenant_id}/relationships/{relationship_id}

# Update a relationship
curl -X PUT http://localhost:8000/tenants/{tenant_id}/relationships/{relationship_id} \
  -H "Content-Type: application/json" \
  -d '{"relationship_type": "blocks"}'

# Delete a relationship
curl -X DELETE http://localhost:8000/tenants/{tenant_id}/relationships/{relationship_id}

# List relationships (with optional filters)
curl "http://localhost:8000/tenants/{tenant_id}/relationships?source_node_id=id&relationship_type=depends_on"
```

## Error Handling

The REST wrapper maps JSON-RPC error codes to HTTP status codes:

| JSON-RPC Error Code | HTTP Status | Description |
|---------------------|-------------|-------------|
| `-32001` | 404 | Not Found |
| `-32602` | 400 | Invalid Parameters (Validation Error) |
| `-32603` | 500 | Internal Error |
| Other | 500 | Internal Server Error |

## Running Tests

```bash
# From the python directory
pip install pytest pytest-asyncio
python -m pytest rest_wrapper/tests/ -v
```

## Running Both Services Together

To run both the JSON-RPC backend and REST wrapper together:

### Terminal 1: Start JSON-RPC Backend

```bash
cd python
./scripts/start.sh
# Or: python main.py
```

### Terminal 2: Start REST Wrapper

```bash
cd python
PYTHONPATH=. uvicorn rest_wrapper.main:app --host 0.0.0.0 --port 8000
```

### Using Docker Compose (Optional)

You can add the REST wrapper to your Docker setup by creating a service:

```yaml
# Add to docker-compose.yml
rest-wrapper:
  build:
    context: python
    dockerfile: Dockerfile.rest
  ports:
    - "8000:8000"
  environment:
    - JSONRPC_URL=http://jsonrpc-backend:5000/jsonrpc
  depends_on:
    - jsonrpc-backend
```

## Development

### Adding New Endpoints

1. Define Pydantic models in `models.py`
2. Create or update router in `routers/`
3. Register router in `main.py`
4. Add tests in `tests/`

### Running with Hot Reload

```bash
PYTHONPATH=. uvicorn rest_wrapper.main:app --reload --port 8000
```

## License

MIT License
