"""
Configuration for REST wrapper.
"""

import os
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Config:
    """REST wrapper configuration."""
    
    # JSON-RPC server URL
    jsonrpc_url: str = "http://localhost:5000/jsonrpc"
    
    # REST server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API metadata for OpenAPI documentation
    title: str = "flex-db REST API"
    description: str = "REST API facade for flex-db JSON-RPC backend"
    version: str = "1.0.0"


def config_from_env() -> Config:
    """Load configuration from environment variables."""
    return Config(
        jsonrpc_url=os.getenv("JSONRPC_URL", "http://localhost:5000/jsonrpc"),
        host=os.getenv("REST_HOST", "0.0.0.0"),
        port=int(os.getenv("REST_PORT", "8000")),
        title=os.getenv("REST_API_TITLE", "flex-db REST API"),
        description=os.getenv("REST_API_DESCRIPTION", "REST API facade for flex-db JSON-RPC backend"),
        version=os.getenv("REST_API_VERSION", "1.0.0"),
    )


# Default configuration instance
default_config = Config()
