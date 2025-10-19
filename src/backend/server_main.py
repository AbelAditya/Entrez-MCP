import asyncio
from mcp.server.stdio import stdio_server

from server.server import create_server



async def main():
    
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    print("Starting MCP server...")
    asyncio.run(main())
