from client.client import EntrezClient

async def interactive_mode():
    """Run an interactive client session"""
    
    # Create client
    client = EntrezClient()
    
    # Use the convenient with_session method
    async def run_interactive(session):
        print("=== Interactive Entrez MCP Client ===")
        print("Available commands:")
        print("  search <db> <term> - Search a database")
        print("  fetch <db> <id> - Fetch records")
        print("  summary <db> <id> - Get summaries")
        print("  info [db] - Get database info")
        print("  tools - List all tools")
        print("  quit - Exit")
        print()
        
        while True:
            try:
                cmd = input("entrez> ").strip()
                if not cmd:
                    continue
                
                parts = cmd.split(maxsplit=2)
                command = parts[0].lower()
                
                if command == "quit":
                    break
                
                elif command == "tools":
                    tools = await session.list_tools()
                    for tool in tools.tools:
                        print(f"{tool.name}: {tool.description}")
                
                elif command == "search" and len(parts) >= 3:
                    db, term = parts[1], parts[2]
                    result = await session.call_tool(
                        "esearch",
                        arguments={"db": db, "term": term, "retmax": 10}
                    )
                    print(result.content[0].text)
                
                elif command == "fetch" and len(parts) >= 3:
                    db, uid = parts[1], parts[2]
                    result = await session.call_tool(
                        "efetch",
                        arguments={"db": db, "id": uid}
                    )
                    print(result.content[0].text)
                
                elif command == "summary" and len(parts) >= 3:
                    db, uid = parts[1], parts[2]
                    result = await session.call_tool(
                        "esummary",
                        arguments={"db": db, "id": uid}
                    )
                    print(result.content[0].text)
                
                elif command == "info":
                    args = {"db": parts[1]} if len(parts) > 1 else {}
                    result = await session.call_tool("einfo", arguments=args)
                    print(result.content[0].text)
                
                else:
                    print("Invalid command. Type 'tools' for help.")
            
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except Exception as e:
                print(f"Error: {e}")
    
    # Execute the interactive session with automatic session management
    await client.with_session(run_interactive)