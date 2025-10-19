from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from utils.config import config
from server.handlers import ToolHandler
from services.entrez import EntrezService

# Create service instance
entrez_service = EntrezService()

# Create handler instance
tool_handler = ToolHandler(entrez_service)


# Create MCP server instance
app = Server(config.server_name)

@app.call_tool()
async def ping(name: str, arguments: Any):
    if name == "ping":
        return [TextContent(type="text", text="pong")]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Entrez tools"""
    return entrez_service.get_available_tools()


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for Entrez operations"""
    return await tool_handler.handle_tool_call(name, arguments)





def create_server() -> Server:
    """Create and configure the MCP server"""
    return app


