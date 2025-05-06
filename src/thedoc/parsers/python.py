"""Python-specific code parser."""

import ast
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import BaseParser, DocItem


class PythonParser(BaseParser):
    """Parser for Python source code."""

    def get_file_extensions(self) -> List[str]:
        """Get Python file extensions."""
        return ['.py']

    def parse_file(self, file_path: Path) -> List[DocItem]:
        """Parse a Python file and extract documentation."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
            items = self._parse_module(tree, str(file_path))
            return [item for item in items if item is not None]
        except SyntaxError:
            print(f"Error parsing {file_path}: Invalid Python syntax")
            return []

    def _parse_module(self, tree: ast.Module, file_path: str) -> List[DocItem]:
        """Parse an AST module node."""
        items = []
        
        module_doc = ast.get_docstring(tree)
        if module_doc:
            items.append(DocItem(
                name=Path(file_path).stem,
                type='module',
                description=module_doc,
                source_file=file_path,
                line_number=1
            ))

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                items.extend(self._parse_class(node, file_path))
            elif isinstance(node, ast.FunctionDef):
                func_item = self._parse_function(node, file_path)
                if func_item:
                    items.append(func_item)

        return items

    def _parse_class(self, node: ast.ClassDef, file_path: str) -> List[DocItem]:
        """Parse a class definition."""
        items = []

        class_doc = ast.get_docstring(node)
        if class_doc:
            items.append(DocItem(
                name=node.name,
                type='class',
                description=class_doc,
                source_file=file_path,
                line_number=node.lineno
            ))

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method = self._parse_function(item, file_path, is_method=True)
                if method:
                    method.name = f"{node.name}.{method.name}"
                    items.append(method)

        return items

    def _parse_function(self, node: ast.FunctionDef, file_path: str, is_method: bool = False) -> Optional[DocItem]:
        """Parse a function definition."""
        doc = ast.get_docstring(node)
        if not doc:
            return None

        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        signature = f"{node.name}({', '.join(args)})"

        params: Dict[str, str] = {}
        returns: Optional[str] = None
        examples: List[str] = []
        description = []
        
        current_section = description
        lines = doc.split('\n')
        
        current_example = []
        in_example = False
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('args:') or line.lower().startswith('parameters:'):
                current_section = []
                in_example = False
            elif line.lower().startswith('returns:'):
                returns = line[8:].strip()
                in_example = False
            elif line.lower().startswith('example:') or line.lower().startswith('examples:'):
                in_example = True
                current_example = []
            elif line and ':' in line and not in_example and current_section != description:
                param, desc = line.split(':', 1)
                params[param.strip()] = desc.strip()
            elif line and in_example:
                current_example.append(line)
            elif not line and in_example and current_example:
                examples.append('\n'.join(current_example))
                current_example = []
            elif line and not in_example:
                current_section.append(line)
        
        if current_example:
            examples.append('\n'.join(current_example))

        return DocItem(
            name=node.name,
            type='method' if is_method else 'function',
            description='\n'.join(description).strip(),
            signature=signature,
            params=params,
            returns=returns,
            examples=examples,
            source_file=file_path,
            line_number=node.lineno
        ) 