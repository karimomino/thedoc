"""Parser for Swift documentation comments."""

import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .base import BaseParser, DocItem

class SwiftParser(BaseParser):
    """Parser for Swift documentation comments."""

    def __init__(self, root_path: Path = None):
        """Initialize the parser."""
        if root_path:
            super().__init__(root_path)
        
        self.doc_pattern = re.compile(
            r'///.*?(?=\n(?!///)|$)|/\*\*.*?\*/',
            re.DOTALL | re.MULTILINE
        )
        
        self.code_line_pattern = re.compile(
            r'\n([^\n]+)',
            re.DOTALL
        )
        
        self.tag_patterns = {
            'Parameters': r'-\s*Parameters?\s*:([^-]*)',
            'Returns': r'-\s*Returns?\s*:([^-]*)',
            'Throws': r'-\s*Throws\s*:([^-]*)',
            'Note': r'-\s*Note\s*:([^-]*)',
            'Warning': r'-\s*Warning\s*:([^-]*)',
            'Important': r'-\s*Important\s*:([^-]*)',
            'SeeAlso': r'-\s*SeeAlso\s*:([^-]*)',
            'Precondition': r'-\s*Precondition\s*:([^-]*)',
            'Postcondition': r'-\s*Postcondition\s*:([^-]*)',
            'Case': r'-\s*Case\s*:([^-]*)',
        }
        
        self.parameter_pattern = re.compile(
            r'-\s*(\w+)\s*:([^-]*)',
            re.DOTALL
        )
        
        self.code_patterns = {
            'class': re.compile(r'(?:public|private|internal|fileprivate\s+)?class\s+(\w+)(?!\s*<)'),
            'function': re.compile(r'(?:(?:public|private|internal|fileprivate)\s+)?func\s+([a-zA-Z_][a-zA-Z0-9_]*)'),
            'property': re.compile(r'(?:private\(set\)\s+)?(?:var|let)\s+(\w+)'),
            'enum': re.compile(r'(?:public|private|internal|fileprivate\s+)?enum\s+(\w+)'),
            'case': re.compile(r'case\s+(\w+)(?:\s*=\s*[^,]+)?'),
            'type': re.compile(r'(?:public|private|internal|fileprivate\s+)?class\s+(\w+)(?:\s*<[^>]*>)?')
        }
        
        self.plural_map = {
            'class': 'classes',
            'function': 'functions',
            'property': 'properties',
            'enum': 'enums',
            'case': 'cases',
            'type': 'types'
        }

    def get_file_extensions(self) -> List[str]:
        """Get Swift file extensions."""
        return ['.swift']

    def parse_file(self, file_path: Path) -> List[DocItem]:
        """Parse a Swift source file and extract documentation.

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
                elif section_type == 'enums':
                    item_type = 'enum'
                elif section_type == 'cases':
                    item_type = 'case'
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
        """Parse a Swift source file and extract documentation as a dictionary.

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
            'enums': [],
            'cases': [],
            'types': []
        }

        lines = content.split('\n')
        line_index = 0
        
        while line_index < len(lines):
            line = lines[line_index]
            
            if line.strip().startswith('///'):
                doc_lines = [line]
                line_index += 1
                
                while line_index < len(lines) and lines[line_index].strip().startswith('///'):
                    doc_lines.append(lines[line_index])
                    line_index += 1
                
                while line_index < len(lines) and not lines[line_index].strip():
                    line_index += 1
                
                if line_index >= len(lines):
                    break
                
                code_line = lines[line_index]
                
                if not code_line.strip().startswith('///') and not code_line.strip().startswith('/**'):
                    doc_text = '\n'.join(doc_lines)
                    self._process_doc_block(doc_text, code_line, documentation)
                
                line_index += 1
            
            elif line.strip().startswith('/**'):
                doc_text = line
                multiline_ended = False
                
                line_index += 1
                while line_index < len(lines) and not multiline_ended:
                    doc_text += '\n' + lines[line_index]
                    if '*/' in lines[line_index]:
                        multiline_ended = True
                    line_index += 1
                
                while line_index < len(lines) and not lines[line_index].strip():
                    line_index += 1
                
                if line_index >= len(lines):
                    break
                
                code_line = lines[line_index]
                
                self._process_doc_block(doc_text, code_line, documentation)
                
                line_index += 1
            else:
                line_index += 1

        return documentation

    def _process_doc_block(self, doc_text, code_line, documentation):
        """Process a documentation block and its associated code line.
        
        Args:
            doc_text: The documentation text
            code_line: The associated code line
            documentation: The documentation dictionary to update
        """
        doc_block = self._parse_doc_block(doc_text)
        
        element_type, name = self._detect_code_element(code_line)
        
        if element_type and name:
            doc_block['name'] = name
            plural_type = self.plural_map[element_type]
            

            if element_type == 'case':
                clean_text = self._clean_description(doc_text)
                lines = clean_text.split('\n')
                for line in lines:
                    if line.strip():
                        doc_block['description'] = line.strip()
                        break
            
            if element_type in ['property', 'function', 'enum', 'type', 'class']:
                clean_text = self._clean_description(doc_text)
                
                sections = re.split(r'\n##\s+', clean_text)
                
                if sections:
                    main_section = sections[0].strip()
                    
                    parts = re.split(r'\n(?=(?:-\s+(?:' + '|'.join(self.tag_patterns.keys()) + r')\s*:))', main_section)
                    if parts:
                        doc_block['description'] = parts[0].strip()
                
                for section in sections[1:]:
                    if not section.strip():
                        continue
                    
                    section_parts = section.split('\n', 1)
                    if len(section_parts) < 2:
                        continue
                    
                    title, content = section_parts
                    title = title.lower()
                    
                    if title == 'example':
                        code_blocks = re.findall(r'```swift\n(.*?)```', content, re.DOTALL)
                        if code_blocks:
                            doc_block['examples'] = [block.strip() for block in code_blocks]
            
            documentation[plural_type].append(doc_block)

    def _parse_doc_block(self, doc_text: str) -> Dict:
        """Parse a documentation block.

        Args:
            doc_text: The documentation text to parse

        Returns:
            Dict containing parsed documentation
        """
        doc_text = self._clean_description(doc_text)
        
        doc_block = {
            'description': '',
            'parameters': [],
            'returns': [],
            'throws': [],
            'notes': [],
            'warnings': [],
            'important': [],
            'see_also': [],
            'preconditions': [],
            'postconditions': [],
            'cases': []
        }
        
        sections = re.split(r'\n##\s+', doc_text)
        
        main_section = sections[0].strip()
        
        parts = re.split(r'\n(?=(?:-\s+(?:' + '|'.join(self.tag_patterns.keys()) + r')\s*:))', main_section)
        if parts:
            description = parts[0].strip()
            doc_block['description'] = description
            
            if len(parts) > 1:
                tags_text = '\n'.join(parts[1:])
                self._parse_tags(tags_text, doc_block)
        
        for section in sections[1:]:
            if not section.strip():
                continue
            
            section_parts = section.split('\n', 1)
            if len(section_parts) < 2:
                continue
                
            title, content = section_parts
            title = title.lower()
            
            if title == 'example':
                code_blocks = re.findall(r'```swift\n(.*?)```', content, re.DOTALL)
                if code_blocks:
                    doc_block['examples'] = [block.strip() for block in code_blocks]
            elif title == 'parameters':
                param_matches = self.parameter_pattern.finditer(content)
                for match in param_matches:
                    doc_block['parameters'].append({
                        'name': match.group(1),
                        'description': match.group(2).strip()
                    })
            elif title == 'cases':
                case_lines = content.strip().split('\n')
                for line in case_lines:
                    case_match = re.match(r'-\s*`(\w+)`\s*:\s*(.+)', line.strip())
                    if case_match:
                        doc_block['cases'].append({
                            'name': case_match.group(1),
                            'description': case_match.group(2).strip()
                        })
        
        return doc_block

    def _parse_tags(self, tags_text: str, doc_block: Dict) -> None:
        """Parse documentation tags and add them to the doc block.

        Args:
            tags_text: The text containing the tags
            doc_block: The documentation block to update
        """
        for tag, pattern in self.tag_patterns.items():
            matches = re.finditer(pattern, tags_text, re.DOTALL)
            for match in matches:
                content = match.group(1).strip()
                if tag == 'Parameters':
                    param_matches = self.parameter_pattern.finditer(content)
                    for param_match in param_matches:
                        doc_block['parameters'].append({
                            'name': param_match.group(1),
                            'description': param_match.group(2).strip()
                        })
                elif tag == 'Case':
                    case_match = re.match(r'(\w+):\s*(.+)', content)
                    if case_match:
                        doc_block['cases'].append({
                            'name': case_match.group(1),
                            'description': case_match.group(2).strip()
                        })
                else:
                    tag_list = tag.lower() + 's'
                    if tag_list in doc_block:
                        doc_block[tag_list].append({'text': content})

    def _detect_code_element(self, code_line: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect the type of Swift code element and its name.

        Args:
            code_line: The line of code following the doc comment

        Returns:
            Tuple of (element_type, element_name) or (None, None) if not detected
        """
        generic_class_match = re.search(r'(?:public\s+|private\s+|internal\s+|fileprivate\s+)?class\s+(\w+)\s*<', code_line)
        if generic_class_match:
            return 'type', generic_class_match.group(1)
        
        for element_type, pattern in self.code_patterns.items():
            match = pattern.search(code_line)
            if match:
                return element_type, match.group(1)
        
        return None, None

    def _clean_description(self, text: str) -> str:
        """Clean up the description text by removing comment markers and extra whitespace.

        Args:
            text: The description text to clean

        Returns:
            Cleaned description text
        """
        if text.startswith('/**'):
            text = re.sub(r'^\s*/\*\*\s*|\s*\*/\s*$', '', text)
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = re.sub(r'^\s*\*\s*', '', line)
                cleaned_lines.append(line.rstrip())
        else:
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = re.sub(r'^\s*///\s*', '', line)
                if not cleaned_lines and not line.strip():
                    continue
                cleaned_lines.append(line.rstrip())
        
        return '\n'.join(cleaned_lines).strip() 