import os

from client.client import EntrezClient
from client.ai_interface import create_ai_client, check_ai_availability
from utils.text_utils import read_text_file

async def ai_mode():
    """Run AI-powered client session with flexible AI backend"""
    
    # Auto-detect and create AI client
    ai_client = create_ai_client()
    if not ai_client:
        print("Error: No AI backend available.")
        print("Please set MISTRAL_KEY or ensure Docker AI is running.")
        return
    
    # Check if AI service is available
    
    if not await check_ai_availability(ai_client):
        print(f"Error: AI service is not available.")
        print("Please check your AI backend configuration.")
        return
    
    print(f"Using AI backend: {type(ai_client).__name__}")
    
    # Create MCP client
    client = EntrezClient()
    
    # Use the convenient with_session method
    async def run_ai(session):
        # Get available tools from server
        tools_response = await session.list_tools()
        tools = [{"name": tool.name, "description": tool.description} for tool in tools_response.tools]

        prompts = [{
            "role": "system",
            "content": read_text_file("text/user-facing/welcome_ai.txt")
        }]

        print("\n")
        print("=== AI-Powered Entrez Client ===")
        print("Ask me anything about biological data!")
        print("Type 'quit()' to exit\n")

        while True:
            try:
                ques =input("Questions: ")

                if ques == "quit()":
                    break

                prompts.append({'role': "user", "content": ques})

                # Use the abstracted AI client
                resp = await ai_client.chat_complete(
                    messages=prompts,
                    tools=tools,
                    tool_choice="any"
                )

                print(f"AI Response: {resp.content}")
                
                # Handle tool calls if present
                if resp.tool_calls:
                    print(f"AI wants to use {len(resp.tool_calls)} tool(s)")
                    
                    # Execute each tool call
                    for tool_call in resp.tool_calls:
                        tool_name = tool_call['function']['name']
                        tool_args = tool_call['function']['arguments']
                        
                        print(f"Executing tool: {tool_name} with args: {tool_args}")
                        
                        # Call the tool via MCP
                        tool_result = await session.call_tool(tool_name, tool_args)
                        print(f"Tool result: {tool_result}")
                        # Add tool result to conversation
                        prompts.append({
                            "role": "assistant", 
                            "content": f"Tool call: {tool_name}({tool_args})"
                        })
                        prompts.append({
                            "role": "tool", 
                            "content": f"Tool result: {tool_result.content}"
                        })
                    
                    # Get AI's response to the tool results
                    final_resp = await ai_client.chat_complete(
                        messages=prompts,
                        tools=tools,
                        tool_choice="none"  # Don't allow more tool calls
                    )
                    print(f"Final AI Response: {final_resp}")
                
            except KeyboardInterrupt:
                print("\nUse 'quit()' to exit")
            except Exception as e:
                print(f"Error: {e}")
    
    # Execute the AI session with automatic session management
    await client.with_session(run_ai)