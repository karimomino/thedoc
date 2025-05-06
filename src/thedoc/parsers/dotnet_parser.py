"""Parser for .NET documentation comments."""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

from .base import BaseParser, DocItem

class DotNetParser(BaseParser):
    """Parser for .NET documentation comments."""

    def __init__(self, root_path: Path = None):
        """Initialize the parser."""
        if root_path:
            super().__init__(root_path)
        
        self.doc_pattern = re.compile(r'///.*?(?=\n(?!\s*///))|<(?:class|interface|method|property|enum|type)[\s\S]*?</(?:class|interface|method|property|enum|type)>', re.DOTALL)

    def get_file_extensions(self) -> List[str]:
        """Get .NET file extensions."""
        return ['.cs', '.vb']

    def parse_file(self, file_path: Path) -> List[DocItem]:
        """Parse a .NET source file and extract documentation.

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
                elif section_type == 'methods':
                    item_type = 'function'
                elif section_type == 'properties':
                    item_type = 'property'
                elif section_type == 'enums':
                    item_type = 'enum'
                elif section_type == 'interfaces':
                    item_type = 'interface'
                elif section_type == 'types':
                    item_type = 'type'
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
        """Parse a .NET source file and extract documentation as a dictionary.

        Args:
            file_path: Path to the source file

        Returns:
            Dict containing parsed documentation
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = self._convert_triple_slash_to_xml(content)

        doc_blocks = self.doc_pattern.findall(content)

        documentation = {
            'classes': [],
            'methods': [],
            'properties': [],
            'enums': [],
            'interfaces': [],
            'types': []
        }

        for block in doc_blocks:
            try:
                root = ET.fromstring(block)
                
                if root.tag == 'class':
                    documentation['classes'].append(self._parse_class(root))
                elif root.tag == 'method':
                    documentation['methods'].append(self._parse_method(root))
                elif root.tag == 'property':
                    documentation['properties'].append(self._parse_property(root))
                elif root.tag == 'enum':
                    documentation['enums'].append(self._parse_enum(root))
                elif root.tag == 'interface':
                    documentation['interfaces'].append(self._parse_interface(root))
                elif root.tag == 'type':
                    documentation['types'].append(self._parse_type(root))
            except ET.ParseError as e:
                print(f"Error parsing documentation block: {e}")
                print(f"Block content:\n{block}")
                continue

        return documentation
        
    def _convert_triple_slash_to_xml(self, content: str) -> str:
        """Convert triple slash comments to XML format.
        
        Args:
            content: The source file content
            
        Returns:
            Source with triple slash comments converted to XML
        """
        lines = content.split('\n')
        
        i = 0
        result = []
        while i < len(lines):
            line = lines[i]
            
            if line.strip().startswith('///'):
                comment_lines = []
                while i < len(lines) and lines[i].strip().startswith('///'):
                    comment_line = lines[i].strip()[3:].strip()
                    comment_lines.append(comment_line)
                    i += 1
                

                if i < len(lines):
                    next_line = lines[i]
                    
                    xml_tag = 'type'
                    if 'class ' in next_line:
                        xml_tag = 'class'
                    elif 'interface ' in next_line:
                        xml_tag = 'interface'
                    elif 'enum ' in next_line:
                        xml_tag = 'enum'
                    elif 'void ' in next_line or ' => ' in next_line or ' return ' in next_line:
                        xml_tag = 'method'
                    elif 'property ' in next_line or 'get;' in next_line or 'set;' in next_line:
                        xml_tag = 'property'
                    
                    name_match = re.search(r'\b([A-Za-z0-9_]+)\b(?=\s*[(:{\s]|$)', next_line)
                    name = name_match.group(1) if name_match else 'Unknown'
                    
                    xml = f"<{xml_tag} name=\"{name}\">\n"
                    
                    summary_lines = []
                    other_lines = []
                    
                    for cline in comment_lines:
                        if cline.startswith('<param') or cline.startswith('<returns') or cline.startswith('<exception'):
                            other_lines.append(cline)
                        else:
                            summary_lines.append(cline)
                    
                    if summary_lines:
                        xml += "<summary>\n"
                        xml += "\n".join(summary_lines)
                        xml += "\n</summary>\n"
                    
                    xml += "\n".join(other_lines)
                    
                    xml += f"\n</{xml_tag}>"
                    
                    result.append(xml)
                    result.append(next_line)
                else:
                    result.extend(comment_lines)
            else:
                result.append(line)
                i += 1
                
        return '\n'.join(result)
    
    def _parse_class(self, element: ET.Element) -> Dict[str, Any]:
        """Parse a class documentation element.
        
        Args:
            element: The XML element containing class documentation
            
        Returns:
            Dictionary with parsed class documentation
        """
        result = {
            'name': element.get('name', 'Unknown'),
            'description': '',
            'params': {},
            'examples': []
        }
        
        summary = element.find('summary')
        if summary is not None:
            result['description'] = ''.join(summary.itertext()).strip()
        
        examples = element.findall('example')
        for example in examples:
            result['examples'].append(''.join(example.itertext()).strip())
        
        return result
    
    def _parse_method(self, element: ET.Element) -> Dict[str, Any]:
        """Parse a method documentation element.
        
        Args:
            element: The XML element containing method documentation
            
        Returns:
            Dictionary with parsed method documentation
        """
        result = {
            'name': element.get('name', 'Unknown'),
            'description': '',
            'params': {},
            'returns': None,
            'examples': []
        }
        
        summary = element.find('summary')
        if summary is not None:
            result['description'] = ''.join(summary.itertext()).strip()
        
        params = element.findall('param')
        for param in params:
            name = param.get('name', 'unknown')
            description = ''.join(param.itertext()).strip()
            result['params'][name] = description
        
        returns = element.find('returns')
        if returns is not None:
            result['returns'] = ''.join(returns.itertext()).strip()
        
        examples = element.findall('example')
        for example in examples:
            result['examples'].append(''.join(example.itertext()).strip())
        
        return result
    
    def _parse_property(self, element: ET.Element) -> Dict[str, Any]:
        """Parse a property documentation element."""
        result = {
            'name': element.get('name', 'Unknown'),
            'description': '',
            'examples': []
        }
        
        summary = element.find('summary')
        if summary is not None:
            result['description'] = ''.join(summary.itertext()).strip()
        
        examples = element.findall('example')
        for example in examples:
            result['examples'].append(''.join(example.itertext()).strip())
        
        return result
    
    def _parse_enum(self, element: ET.Element) -> Dict[str, Any]:
        """Parse an enum documentation element."""
        return {
            'name': element.get('name', 'Unknown'),
            'description': self._get_summary_text(element),
            'values': {}
        }
    
    def _parse_interface(self, element: ET.Element) -> Dict[str, Any]:
        """Parse an interface documentation element."""
        return {
            'name': element.get('name', 'Unknown'),
            'description': self._get_summary_text(element)
        }
    
    def _parse_type(self, element: ET.Element) -> Dict[str, Any]:
        """Parse a type documentation element."""
        return {
            'name': element.get('name', 'Unknown'),
            'description': self._get_summary_text(element)
        }
    
    def _get_summary_text(self, element: ET.Element) -> str:
        """Get the summary text from an element."""
        summary = element.find('summary')
        if summary is not None:
            return ''.join(summary.itertext()).strip()
        return '' 