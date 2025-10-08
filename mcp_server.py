#!/usr/bin/env python3
"""
MCP Server for NCBI Entrez
Provides access to NCBI databases through the Entrez E-utilities
"""

import asyncio
import os
from typing import Any, Optional
from urllib.parse import urlencode
import aiohttp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Entrez base URL
ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Get API key from environment (optional but recommended)
API_KEY = os.getenv("ENTREZ_API_KEY")

app = Server("entrez-mcp-server")

async def make_entrez_request(
    endpoint: str, params: dict[str, Any]
) -> str:
    """Make an async request to NCBI Entrez API"""
    if API_KEY:
        params["api_key"] = API_KEY
    
    url = f"{ENTREZ_BASE}/{endpoint}.fcgi"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.text()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Entrez tools"""
    return [
        Tool(
            name="esearch",
            description="Search an NCBI database and retrieve a list of UIDs matching the query. "
                       "Databases include: pubmed, protein, nuccore, nucleotide, gene, genome, and more. "
                       "Returns up to retmax results (default 20, max 100000).",
            inputSchema={
                "type": "object",
                "properties": {
                    "db": {
                        "type": "string",
                        "description": "Database to search (e.g., 'pubmed', 'protein', 'gene', 'nuccore')",
                    },
                    "term": {
                        "type": "string",
                        "description": "Search query using Entrez search syntax",
                    },
                    "retmax": {
                        "type": "integer",
                        "description": "Maximum number of UIDs to return (default: 20)",
                        "default": 20,
                    },
                    "retstart": {
                        "type": "integer",
                        "description": "Starting index for results (default: 0)",
                        "default": 0,
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order (e.g., 'relevance', 'pub_date')",
                    },
                },
                "required": ["db", "term"],
            },
        ),
        Tool(
            name="efetch",
            description="Retrieve formatted data records from an NCBI database using UIDs. "
                       "Returns full records in various formats (xml, json, text, fasta, gb, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "db": {
                        "type": "string",
                        "description": "Database name (e.g., 'pubmed', 'protein', 'nuccore')",
                    },
                    "id": {
                        "type": "string",
                        "description": "Comma-separated list of UIDs to fetch",
                    },
                    "rettype": {
                        "type": "string",
                        "description": "Retrieval type (e.g., 'abstract', 'fasta', 'gb', 'xml')",
                    },
                    "retmode": {
                        "type": "string",
                        "description": "Retrieval mode ('xml', 'text', 'json')",
                        "default": "xml",
                    },
                },
                "required": ["db", "id"],
            },
        ),
        Tool(
            name="esummary",
            description="Retrieve document summaries (DocSums) from an NCBI database using UIDs. "
                       "Returns condensed information about records.",
            inputSchema={
                "type": "object",
                "properties": {
                    "db": {
                        "type": "string",
                        "description": "Database name",
                    },
                    "id": {
                        "type": "string",
                        "description": "Comma-separated list of UIDs",
                    },
                    "retmode": {
                        "type": "string",
                        "description": "Return mode ('xml' or 'json')",
                        "default": "json",
                    },
                },
                "required": ["db", "id"],
            },
        ),
        Tool(
            name="einfo",
            description="Get information about available Entrez databases or detailed field information "
                       "for a specific database. Call without db parameter to list all databases.",
            inputSchema={
                "type": "object",
                "properties": {
                    "db": {
                        "type": "string",
                        "description": "Database name (optional - omit to list all databases)",
                    },
                    "retmode": {
                        "type": "string",
                        "description": "Return mode ('xml' or 'json')",
                        "default": "json",
                    },
                },
            },
        ),
        Tool(
            name="elink",
            description="Retrieve UIDs of related records in the same or different databases, "
                       "or retrieve linkout URLs. Useful for finding related articles, genes, proteins, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dbfrom": {
                        "type": "string",
                        "description": "Source database",
                    },
                    "db": {
                        "type": "string",
                        "description": "Target database (can be same as dbfrom)",
                    },
                    "id": {
                        "type": "string",
                        "description": "Comma-separated list of UIDs from source database",
                    },
                    "linkname": {
                        "type": "string",
                        "description": "Specific link name (optional)",
                    },
                    "retmode": {
                        "type": "string",
                        "description": "Return mode ('xml' or 'json')",
                        "default": "json",
                    },
                },
                "required": ["dbfrom", "db", "id"],
            },
        ),
        Tool(
            name="egquery",
            description="Provides counts of search results across all Entrez databases for a single query. "
                       "Useful for determining which databases contain relevant results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": "Search query",
                    },
                },
                "required": ["term"],
            },
        ),
        Tool(
            name="espell",
            description="Retrieve spelling suggestions for a text query in a specific database. "
                       "Helps correct misspelled search terms.",
            inputSchema={
                "type": "object",
                "properties": {
                    "db": {
                        "type": "string",
                        "description": "Database name",
                    },
                    "term": {
                        "type": "string",
                        "description": "Search query to check spelling",
                    },
                },
                "required": ["db", "term"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for Entrez operations"""
    
    try:
        if name == "esearch":
            params = {
                "db": arguments["db"],
                "term": arguments["term"],
                "retmax": arguments.get("retmax", 20),
                "retstart": arguments.get("retstart", 0),
                "retmode": "json",
            }
            if "sort" in arguments:
                params["sort"] = arguments["sort"]
            
            result = await make_entrez_request("esearch", params)
            return [TextContent(type="text", text=result)]
        
        elif name == "efetch":
            params = {
                "db": arguments["db"],
                "id": arguments["id"],
                "retmode": arguments.get("retmode", "xml"),
            }
            if "rettype" in arguments:
                params["rettype"] = arguments["rettype"]
            
            result = await make_entrez_request("efetch", params)
            return [TextContent(type="text", text=result)]
        
        elif name == "esummary":
            params = {
                "db": arguments["db"],
                "id": arguments["id"],
                "retmode": arguments.get("retmode", "json"),
            }
            
            result = await make_entrez_request("esummary", params)
            return [TextContent(type="text", text=result)]
        
        elif name == "einfo":
            params = {"retmode": arguments.get("retmode", "json")}
            if "db" in arguments:
                params["db"] = arguments["db"]
            
            result = await make_entrez_request("einfo", params)
            return [TextContent(type="text", text=result)]
        
        elif name == "elink":
            params = {
                "dbfrom": arguments["dbfrom"],
                "db": arguments["db"],
                "id": arguments["id"],
                "retmode": arguments.get("retmode", "json"),
            }
            if "linkname" in arguments:
                params["linkname"] = arguments["linkname"]
            
            result = await make_entrez_request("elink", params)
            return [TextContent(type="text", text=result)]
        
        elif name == "egquery":
            params = {
                "term": arguments["term"],
            }
            
            result = await make_entrez_request("egquery", params)
            return [TextContent(type="text", text=result)]
        
        elif name == "espell":
            params = {
                "db": arguments["db"],
                "term": arguments["term"],
            }
            
            result = await make_entrez_request("espell", params)
            return [TextContent(type="text", text=result)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())