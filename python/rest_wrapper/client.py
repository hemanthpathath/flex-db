"""
JSON-RPC client for forwarding requests from REST endpoints.
"""

import logging
from typing import Any, Dict, Optional
import httpx

from rest_wrapper.config import Config

logger = logging.getLogger(__name__)


class JSONRPCError(Exception):
    """Exception for JSON-RPC errors."""
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"JSON-RPC Error {code}: {message}")


class JSONRPCClient:
    """Async client for JSON-RPC server."""
    
    def __init__(self, url: str):
        """Initialize the client with the JSON-RPC server URL."""
        self.url = url
        self._request_id = 0
    
    def _next_request_id(self) -> int:
        """Generate the next request ID."""
        self._request_id += 1
        return self._request_id
    
    async def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Call a JSON-RPC method.
        
        Args:
            method: The JSON-RPC method name
            params: The method parameters
            
        Returns:
            The result from the JSON-RPC response
            
        Raises:
            JSONRPCError: If the JSON-RPC call returns an error
        """
        request_id = self._next_request_id()
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id,
        }
        
        logger.debug(f"JSON-RPC request: {payload}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
        
        logger.debug(f"JSON-RPC response: {result}")
        
        if "error" in result:
            error = result["error"]
            raise JSONRPCError(error.get("code", -32603), error.get("message", "Unknown error"))
        
        return result.get("result", {})


# Global client instance (to be initialized on startup)
_client: Optional[JSONRPCClient] = None


def get_client() -> JSONRPCClient:
    """Get the global JSON-RPC client instance."""
    if _client is None:
        raise RuntimeError("JSON-RPC client not initialized. Call init_client() first.")
    return _client


def init_client(config: Config) -> JSONRPCClient:
    """Initialize the global JSON-RPC client."""
    global _client
    _client = JSONRPCClient(config.jsonrpc_url)
    return _client
