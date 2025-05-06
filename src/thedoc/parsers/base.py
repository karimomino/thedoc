"""Base parser for code analysis."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DocItem:
    """Represents a documentation item."""
    name: str
    type: str
    description: str
    signature: Optional[str] = None
    params: Dict[str, str] = None
    returns: Optional[str] = None
    examples: List[str] = None
    source_file: Optional[str] = None
    line_number: Optional[int] = None

    def __post_init__(self):
        """Initialize optional fields."""
        self.params = self.params or {}
        self.examples = self.examples or []


class BaseParser(ABC):
    """Base class for language-specific parsers."""

    def __init__(self, root_path: Path):
        """Initialize the parser.
        
        Args:
            root_path: The root path of the project to parse.
        """
        self.root_path = root_path

    @abstractmethod
    def parse_file(self, file_path: Path) -> List[DocItem]:
        """Parse a single file and extract documentation items.
        
        Args:
            file_path: Path to the file to parse.
            
        Returns:
            List of documentation items found in the file.
        """
        pass

    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """Get the file extensions this parser can handle.
        
        Returns:
            List of file extensions (e.g., ['.py', '.pyx']).
        """
        pass

    def is_supported_file(self, file_path: Path) -> bool:
        """Check if the given file is supported by this parser.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            True if the file is supported, False otherwise.
        """
        return file_path.suffix.lower() in self.get_file_extensions()

    def parse_directory(self, directory: Path) -> List[DocItem]:
        """Parse all supported files in a directory recursively.
        
        Args:
            directory: Path to the directory to parse.
            
        Returns:
            List of documentation items found in all supported files.
        """
        items = []
        for file_path in directory.rglob("*"):
            if file_path.is_file() and self.is_supported_file(file_path):
                items.extend(self.parse_file(file_path))
        return items 