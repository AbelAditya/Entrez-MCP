import asyncio

from client.app import main

if __name__ == "__main__":
    print("Starting MCP client...")
    asyncio.run(main())