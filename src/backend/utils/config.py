import os
from dataclasses import dataclass
from typing import Literal, Optional
from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration for the Entrez MCP server"""
    
    # Entrez API Configuration
    entrez_base: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    entrez_api_key: Optional[str] = None
    
    # LLM Configuration
    llm_api_key: Optional[str] = None
    llm_model: Literal["ollama", "hosted"] = "ollama"
    
    # Server Configuration
    server_name: str = "entrez-mcp-server"
    
    def __post_init__(self):
        """Load API keys from environment and .env files if not provided"""
        load_dotenv()
        
        if self.entrez_api_key is None:
            self.entrez_api_key = os.getenv("ENTREZ_API_KEY")
        
        if self.llm_model == "hosted" and self.llm_api_key is None:
            self.llm_api_key = os.getenv("LLM_API_KEY")


# Global config instance
config = Config()
