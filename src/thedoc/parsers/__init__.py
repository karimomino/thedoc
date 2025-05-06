"""TheDoc parsers package."""

from .base import BaseParser, DocItem
from .python import PythonParser

__all__ = ['BaseParser', 'DocItem', 'PythonParser'] 