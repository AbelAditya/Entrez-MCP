"""
Text Utilities
Helper functions for reading text files and managing prompts
"""

from pathlib import Path
from typing import Optional


def read_text_file(path :str) -> str:
    """
    Read text content from a file
    
    Args:
        path: Path to the file to read
    Returns:
        Content of the file as string
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

