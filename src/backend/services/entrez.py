"""
Entrez API Service
Handles all communication with NCBI Entrez E-utilities
"""

import aiohttp
from pathlib import Path
from typing import Any, Dict, Optional, List
from mcp.types import Tool
from utils.config import config
from utils.registry import ToolRegistry


class EntrezService:
    """Service for interacting with NCBI Entrez E-utilities"""
    
    def __init__(self):
        self.base_url = config.entrez_base
        self.api_key = config.entrez_api_key
        
        # Initialize tool registry
        tools_path = Path(__file__).parent.parent / "tools" / "definitions.json"
        self.registry = ToolRegistry(str(tools_path))
    
    def get_available_tools(self) -> List[Tool]:
        """Get list of available tools for this service"""
        return self.registry.get_tools()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Make an async request to NCBI Entrez API"""
        # Add API key if available
        if self.api_key:
            params["api_key"] = self.api_key
        
        url = f"{self.base_url}/{endpoint}.fcgi"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.text()
    
    async def search(self, db: str, term: str, **kwargs) -> str:
        """Search an NCBI database"""
        params = {
            "db": db,
            "term": term,
            "retmax": kwargs.get("retmax", 20),
            "retstart": kwargs.get("retstart", 0),
            "retmode": "json",
        }
        
        if "sort" in kwargs:
            params["sort"] = kwargs["sort"]
        
        return await self._make_request("esearch", params)
    
    async def fetch(self, db: str, ids: str, **kwargs) -> str:
        """Fetch records from an NCBI database"""
        params = {
            "db": db,
            "id": ids,
            "retmode": kwargs.get("retmode", "xml"),
        }
        
        if "rettype" in kwargs:
            params["rettype"] = kwargs["rettype"]
        
        return await self._make_request("efetch", params)
    
    async def summary(self, db: str, ids: str, **kwargs) -> str:
        """Get document summaries from an NCBI database"""
        params = {
            "db": db,
            "id": ids,
            "retmode": kwargs.get("retmode", "json"),
        }
        
        return await self._make_request("esummary", params)
    
    async def info(self, db: Optional[str] = None, **kwargs) -> str:
        """Get database information"""
        params = {
            "retmode": kwargs.get("retmode", "json"),
        }
        
        if db:
            params["db"] = db
        
        return await self._make_request("einfo", params)
    
    async def link(self, dbfrom: str, db: str, ids: str, **kwargs) -> str:
        """Get related records between databases"""
        params = {
            "dbfrom": dbfrom,
            "db": db,
            "id": ids,
            "retmode": kwargs.get("retmode", "json"),
        }
        
        if "linkname" in kwargs:
            params["linkname"] = kwargs["linkname"]
        
        return await self._make_request("elink", params)
    
    async def global_query(self, term: str) -> str:
        """Search across all Entrez databases"""
        params = {"term": term}
        return await self._make_request("egquery", params)
    
    async def spell(self, db: str, term: str) -> str:
        """Get spelling suggestions for a query"""
        params = {
            "db": db,
            "term": term,
        }
        return await self._make_request("espell", params)
