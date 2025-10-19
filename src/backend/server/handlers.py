"""
Tool Handlers
Handles routing tool calls to appropriate services
"""

from typing import Any
from mcp.types import TextContent
from services.entrez import EntrezService


class ToolHandler:
    """Handles routing tool calls to appropriate services"""
    
    def __init__(self, entrez_service: EntrezService):
        self.entrez_service = entrez_service
    
    async def handle_tool_call(self, name: str, arguments: Any) -> list[TextContent]:
        """Route tool calls to appropriate service methods"""
        try:
            # Route tool calls to service methods
            if name == "esearch":
                result = await self.entrez_service.search(
                    db=arguments["db"],
                    term=arguments["term"],
                    **{k: v for k, v in arguments.items() if k not in ["db", "term"]}
                )
            elif name == "efetch":
                result = await self.entrez_service.fetch(
                    db=arguments["db"],
                    ids=arguments["id"],
                    **{k: v for k, v in arguments.items() if k not in ["db", "id"]}
                )
            elif name == "esummary":
                result = await self.entrez_service.summary(
                    db=arguments["db"],
                    ids=arguments["id"],
                    **{k: v for k, v in arguments.items() if k not in ["db", "id"]}
                )
            elif name == "einfo":
                result = await self.entrez_service.info(
                    db=arguments.get("db"),
                    **{k: v for k, v in arguments.items() if k != "db"}
                )
            elif name == "elink":
                result = await self.entrez_service.link(
                    dbfrom=arguments["dbfrom"],
                    db=arguments["db"],
                    ids=arguments["id"],
                    **{k: v for k, v in arguments.items() if k not in ["dbfrom", "db", "id"]}
                )
            elif name == "egquery":
                result = await self.entrez_service.global_query(term=arguments["term"])
            elif name == "espell":
                result = await self.entrez_service.spell(
                    db=arguments["db"],
                    term=arguments["term"]
                )
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]