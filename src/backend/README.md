# Backend Setup

This directory contains the MCP (Model Context Protocol) backend implementation for the Entrez API integration.

## File Organization

- **`client_main.py`** - Main entrypoint for starting the MCP client (primary way to run the application)
- **`server_main.py`** - Testing entrypoint for running the MCP server directly (for development/testing only)
- **`client/`** - MCP client implementation and AI interface components. Currently supports two modes: interactive and ai mode; additionally, the examples.py file runs a pre-defined number of tool calls, serving as test.
- **`server/`** - MCP server implementation with tool handlers. Responsible for server-side logic of calling the tools as well as server-side error handling. The ToolHandler gathers the respective supported services to execute tools no (For now contains only Entrez features but might be extended e.g. by additional database calls or sth?)
- **`services/`** - Core logic of the supporteD tools and how they are to be executed. Classes defined in here are used by the ToolHandler to ultimately gather and use the tools. 
- **`tools/`** - Tool definitions and configurations in json format.
- **`utils/`** - Utility functions and shared components

## Usage

Run the client in ai mode:
```bash
python src/backend/client_main.py --ai
```
This will start the client, which in turn starts the server. If a .env file with a MISTRAL_API_KEY exists, the client will be started as a MistralClient, otherwise a DockerAIClient leveraging ollama will be created.