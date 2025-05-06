"""Parser for Kotlin documentation comments."""

import re
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base import BaseParser, DocItem

class KotlinParser(BaseParser):
    """Parser for Kotlin documentation comments."""

    def __init__(self, root_path: Path = None):
        """Initialize the parser."""
        if root_path:
            super().__init__(root_path)
        
        self.doc_pattern = re.compile(
            r'/\*\*.*?\*/\s*([^\n]*)',
            re.DOTALL
        )
        
        self.tag_patterns = {
            'param': r'@param\s+(\w+)\s+([^\n@]*)',
            'return': r'@return\s+([^\n@]*)',
            'throws': r'@throws\s+(\w+)\s+([^\n@]*)',
            'exception': r'@exception\s+(\w+)\s+([^\n@]*)',
            'see': r'@see\s+([^\n@]*)',
            'author': r'@author\s+([^\n@]*)',
            'since': r'@since\s+([^\n@]*)',
            'sample': r'@sample\s+([^\n@]*)',
        }
        
        self.code_patterns = {
            'class': re.compile(r'(?:public|private|internal|protected)?\s*(?:data|sealed|open|abstract)?\s*class\s+(\w+)'),
            'function': re.compile(r'(?:public|private|internal|protected)?\s*fun\s+(\w+)'),
            'property': re.compile(r'(?:public|private|internal|protected|const)?\s*(?:val|var)\s+(\w+)'),
            'interface': re.compile(r'(?:public|private|internal|protected)?\s*interface\s+(\w+)'),
            'enum': re.compile(r'(?:public|private|internal|protected)?\s*enum\s+class\s+(\w+)'),
            'object': re.compile(r'(?:public|private|internal|protected)?\s*object\s+(\w+)')
        }

    def get_file_extensions(self) -> List[str]:
        """Get Kotlin file extensions."""
        return ['.kt', '.kts']

    def parse_file(self, file_path: Path) -> List[DocItem]:
        """Parse a Kotlin source file and extract documentation.

        Args:
            file_path: Path to the source file

        Returns:
            List of documentation items
        """
        if isinstance(file_path, Path):
            file_path_str = str(file_path)
        else:
            file_path_str = file_path
        
        doc_dict = self._parse_file_to_dict(file_path_str)
        
        doc_items = []
        
        for section_type, items in doc_dict.items():
            for item in items:
                if section_type == 'classes':
                    item_type = 'class'
                elif section_type == 'functions':
                    item_type = 'function'
                elif section_type == 'properties':
                    item_type = 'property'
                elif section_type == 'interfaces':
                    item_type = 'interface'
                elif section_type == 'enums':
                    item_type = 'enum'
                elif section_type == 'objects':
                    item_type = 'object'
                else:
                    item_type = 'unknown'
                
                doc_item = DocItem(
                    name=item.get('name', 'Unknown'),
                    type=item_type,
                    description=item.get('description', ''),
                    signature=item.get('signature', None),
                    params=item.get('params', {}),
                    returns=item.get('returns', None),
                    examples=item.get('examples', []),
                    source_file=file_path_str,
                    line_number=None
                )
                
                doc_items.append(doc_item)
        
        return doc_items

    def _parse_file_to_dict(self, file_path: str) -> Dict:
        """Parse a Kotlin source file and extract documentation as a dictionary.

        Args:
            file_path: Path to the source file

        Returns:
            Dict containing parsed documentation
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        documentation = {
            'classes': [],
            'functions': [],
            'properties': [],
            'interfaces': [],
            'enums': [],
            'objects': []
        }

        matches = self.doc_pattern.finditer(content)

        for match in matches:
            doc_comment = match.group(0)
            code_line = match.group(1) if len(match.groups()) > 0 else ""
            
            doc_block = self._parse_doc_block(doc_comment)
            
            element_type, name = self._detect_code_element(code_line)
            
            if element_type and name:
                doc_block['name'] = name
                
                if element_type == 'class':
                    documentation['classes'].append(doc_block)
                elif element_type == 'function':
                    documentation['functions'].append(doc_block)
                elif element_type == 'property':
                    documentation['properties'].append(doc_block)
                elif element_type == 'interface':
                    documentation['interfaces'].append(doc_block)
                elif element_type == 'enum':
                    documentation['enums'].append(doc_block)
                elif element_type == 'object':
                    documentation['objects'].append(doc_block)

        return documentation
    
    def _parse_doc_block(self, doc_text: str) -> Dict[str, Any]:
        """Parse a KDoc comment block.
        
        Args:
            doc_text: The documentation text
            
        Returns:
            Dictionary with parsed documentation
        """
        doc_text = re.sub(r'/\*\*|\*/|^\s*\*', '', doc_text, flags=re.MULTILINE)
        doc_text = re.sub(r'^\s*', '', doc_text, flags=re.MULTILINE)
        
        description_match = re.search(r'^(.*?)(?=@|$)', doc_text, re.DOTALL)
        description = description_match.group(1).strip() if description_match else ""
        
        doc_block = {
            'description': description,
            'params': {},
            'returns': None,
            'throws': {},
            'examples': []
        }
        
        param_matches = re.finditer(self.tag_patterns['param'], doc_text)
        for match in param_matches:
            param_name = match.group(1)
            param_desc = match.group(2).strip()
            doc_block['params'][param_name] = param_desc
        
        return_match = re.search(self.tag_patterns['return'], doc_text)
        if return_match:
            doc_block['returns'] = return_match.group(1).strip()
        
        throws_matches = re.finditer(self.tag_patterns['throws'], doc_text)
        for match in throws_matches:
            exception_type = match.group(1)
            exception_desc = match.group(2).strip()
            doc_block['throws'][exception_type] = exception_desc
            
        exception_matches = re.finditer(self.tag_patterns['exception'], doc_text)
        for match in exception_matches:
            exception_type = match.group(1)
            exception_desc = match.group(2).strip()
            doc_block['throws'][exception_type] = exception_desc
        
        sample_matches = re.finditer(self.tag_patterns['sample'], doc_text)
        for match in sample_matches:
            doc_block['examples'].append(match.group(1).strip())
        
        return doc_block
    
    def _detect_code_element(self, code_line: str) -> tuple:
        """Detect the type of code element and its name.
        
        Args:
            code_line: The code line following the documentation
            
        Returns:
            Tuple of (element_type, name)
        """
        if not code_line:
            return None, None
            
        for element_type, pattern in self.code_patterns.items():
            match = pattern.search(code_line)
            if match:
                return element_type, match.group(1)
                
        return None, None 