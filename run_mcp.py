"""
Entry point for running the MCP server via FastMCP CLI.

From project root:
  fastmcp run run_mcp.py:mcp

Or run with stdio directly:
  python -m src.server
"""
from src.server import mcp
