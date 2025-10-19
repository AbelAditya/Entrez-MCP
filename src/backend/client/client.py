from typing import List, Any, Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool


class EntrezClient:
    """Core client for interacting with Entrez MCP server"""
    
    def __init__(self, server_path: str = "src/backend/server_main.py"):
        print("Initializing Entrez client...")
        self.server_path = server_path
    
    def create_session(self):
        """Create a new session to the MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path],
        )
        
        # Return the stdio_client context manager
        return stdio_client(server_params)
    
    async def with_session(self, callback):
        """Execute a callback with a session, handling all the connection logic"""
        stdio_client = self.create_session()
        
        async with stdio_client as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await callback(session)
    
    async def list_tools(self, session: ClientSession) -> List[Tool]:
        """Get list of available tools"""
        response = await session.list_tools()
        return response.tools
    
    async def call_tool(self, session: ClientSession, name: str, arguments: Dict[str, Any]):
        """Call a tool with given arguments"""
        response = await session.call_tool(name, arguments)
        return response
