"""
MCP Server Entry Point
Simple entry point that starts the Entrez MCP server
"""
import sys
import os

import asyncio
from mcp.server.stdio import stdio_server

from server.server import create_server
from utils.config import config




async def main():
    """Main entry point for the MCP server"""
    # Create and configure the server
    
    server = create_server()
    # Start the server with stdio
    async with stdio_server() as (read_stream, write_stream):
        
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    print("Starting MCP server...")
    asyncio.run(main())
