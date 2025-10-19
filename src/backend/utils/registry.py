"""
Tool Registry Class
Handles loading and managing tool definitions from JSON
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from mcp.types import Tool


class ToolRegistry:
    """Registry for managing tool definitions"""
    
    def __init__(self, definitions_path: Optional[str] = None):
        self.definitions_path = Path(definitions_path) if definitions_path else None
        self._tools_cache: Optional[List[Tool]] = None
    
    def load_tools_from_json(self, file_path: str) -> List[Tool]:
        """Load tools from JSON file and convert to MCP Tool objects"""
        with open(file_path, 'r') as f:
            data = json.load(f)
            tools_data = data.get("tools", [])
        
        return [
            Tool(
                name=tool_data["name"],
                description=tool_data["description"],
                inputSchema=tool_data["inputSchema"]
            )
            for tool_data in tools_data
        ]
    
    def get_tools(self, definitions_path: Optional[str] = None) -> List[Tool]:
        """Get tools, using cache if available"""
        if self._tools_cache is None:
            path = definitions_path or self.definitions_path
            if path is None:
                raise ValueError("No definitions path provided")
            self._tools_cache = self.load_tools_from_json(str(path))
        return self._tools_cache
    
    def clear_cache(self):
        """Clear the tools cache to force reload"""
        self._tools_cache = None
