"""
MCP (Model Context Protocol) Integration
Legal Advisory System v6.5

Provides standardized protocol layer for AI-to-data integration.
Wraps existing v6 components (logic tree, calculators, validators) as MCP resources and tools.
"""

from backend.mcp.servers.legal_mcp_server import create_legal_mcp_server

__all__ = ["create_legal_mcp_server"]
