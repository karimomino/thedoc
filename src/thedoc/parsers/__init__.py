"""Parser package for TheDoc."""

from .base import BaseParser, DocItem
from .python import PythonParser
from .swift_parser import SwiftParser
from .kotlin_parser import KotlinParser
from .dotnet_parser import DotNetParser

__all__ = [
    'BaseParser',
    'DocItem',
    'PythonParser',
    'SwiftParser',
    'KotlinParser',
    'DotNetParser',
] 