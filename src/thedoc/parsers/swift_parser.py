"""Parser for Swift documentation comments."""

import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .base import BaseParser, DocItem

class SwiftParser(BaseParser):
    """Parser for Swift documentation comments."""

    def __init__(self, root_path: Path = None):
        """Initialize the parser."""
        # Initialize base class if root_path is provided
        if root_path:
            super().__init__(root_path)
        
        # Pattern to match Swift doc comments and the following code
        self.doc_pattern = re.compile(
            r'///.*?(?=\n(?!///)|$)|/\*\*.*?\*/',
            re.DOTALL | re.MULTILINE
        )
        
        # Pattern to match the code line after doc comments
        self.code_line_pattern = re.compile(
            r'\n([^\n]+)',
            re.DOTALL
        )
        
        # Patterns for different Swift doc tags
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
        
        # Pattern for parameter items
        self.parameter_pattern = re.compile(
            r'-\s*(\w+)\s*:([^-]*)',
            re.DOTALL
        )
        
        # Patterns for Swift code elements
        self.code_patterns = {
            'class': re.compile(r'(?:public|private|internal|fileprivate\s+)?class\s+(\w+)(?!\s*<)'),  # Match any access level or none
            'function': re.compile(r'(?:(?:public|private|internal|fileprivate)\s+)?func\s+([a-zA-Z_][a-zA-Z0-9_]*)'),  # Explicitly match valid function names
            'property': re.compile(r'(?:private\(set\)\s+)?(?:var|let)\s+(\w+)'),  # Properties can have any access level
            'enum': re.compile(r'(?:public|private|internal|fileprivate\s+)?enum\s+(\w+)'),  # Match any access level or none
            'case': re.compile(r'case\s+(\w+)(?:\s*=\s*[^,]+)?'),  # Cases don't have access levels
            'type': re.compile(r'(?:public|private|internal|fileprivate\s+)?class\s+(\w+)(?:\s*<[^>]*>)?')  # Match generic classes with full name
        }
        
        # Mapping of element types to their plural forms
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
        # Convert Path to string if needed
        if isinstance(file_path, Path):
            file_path_str = str(file_path)
        else:
            file_path_str = file_path
            
        # Get the parsed dict from the original method
        doc_dict = self._parse_file_to_dict(file_path_str)
        
        # Convert to DocItem list
        doc_items = []
        
        # Process each section in the documentation dictionary
        for section_type, items in doc_dict.items():
            for item in items:
                # Map the item type based on section name
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
                
                # Create DocItem from the dictionary entry
                doc_item = DocItem(
                    name=item.get('name', 'Unknown'),
                    type=item_type,
                    description=item.get('description', ''),
                    signature=item.get('signature', None),
                    params=item.get('params', {}),
                    returns=item.get('returns', None),
                    examples=item.get('examples', []),
                    source_file=file_path_str,
                    line_number=None  # Swift parser doesn't track line numbers
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

        # Split the content into lines
        lines = content.split('\n')
        line_index = 0
        
        # Collect documentation blocks
        while line_index < len(lines):
            line = lines[line_index]
            
            # Check if this is the start of a doc comment (/// style)
            if line.strip().startswith('///'):
                # Start collecting the doc block
                doc_lines = [line]
                line_index += 1
                
                # Continue collecting doc lines
                while line_index < len(lines) and lines[line_index].strip().startswith('///'):
                    doc_lines.append(lines[line_index])
                    line_index += 1
                
                # Skip empty lines
                while line_index < len(lines) and not lines[line_index].strip():
                    line_index += 1
                
                # If we've reached the end of the file, break
                if line_index >= len(lines):
                    break
                
                # Get the code line
                code_line = lines[line_index]
                
                # Process doc block and code line if not another doc comment
                if not code_line.strip().startswith('///') and not code_line.strip().startswith('/**'):
                    doc_text = '\n'.join(doc_lines)
                    self._process_doc_block(doc_text, code_line, documentation)
                
                # Always increment to next line
                line_index += 1
            
            # Check if this is the start of a multiline doc comment (/** style)
            elif line.strip().startswith('/**'):
                # Collect the entire multiline comment
                doc_text = line
                multiline_ended = False
                
                # Keep collecting lines until we find */
                line_index += 1
                while line_index < len(lines) and not multiline_ended:
                    doc_text += '\n' + lines[line_index]
                    if '*/' in lines[line_index]:
                        multiline_ended = True
                    line_index += 1
                
                # Skip empty lines
                while line_index < len(lines) and not lines[line_index].strip():
                    line_index += 1
                
                # If we've reached the end of the file, break
                if line_index >= len(lines):
                    break
                
                # Get the code line
                code_line = lines[line_index]
                
                # Process doc block and code line
                self._process_doc_block(doc_text, code_line, documentation)
                
                # Always increment to next line
                line_index += 1
            else:
                # Not a doc comment, move to next line
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
        
        # Determine the type of code element
        element_type, name = self._detect_code_element(code_line)
        
        if element_type and name:
            doc_block['name'] = name
            plural_type = self.plural_map[element_type]
            
            # For cases, use the first line as description
            if element_type == 'case':
                # Clean the documentation text first
                clean_text = self._clean_description(doc_text)
                # Use the first non-empty line as description
                lines = clean_text.split('\n')
                for line in lines:
                    if line.strip():
                        doc_block['description'] = line.strip()
                        break
            
            # For properties and functions, preserve the description structure
            if element_type in ['property', 'function', 'enum', 'type', 'class']:
                # Clean the documentation text
                clean_text = self._clean_description(doc_text)
                
                # Split into sections by markdown headers
                sections = re.split(r'\n##\s+', clean_text)
                
                # Use first section as description
                if sections:
                    main_section = sections[0].strip()
                    
                    # Split into description and tags
                    parts = re.split(r'\n(?=(?:-\s+(?:' + '|'.join(self.tag_patterns.keys()) + r')\s*:))', main_section)
                    if parts:
                        # First part is the description
                        doc_block['description'] = parts[0].strip()
                
                # Process sections to extract examples
                for section in sections[1:]:
                    if not section.strip():
                        continue
                    
                    section_parts = section.split('\n', 1)
                    if len(section_parts) < 2:
                        continue
                    
                    title, content = section_parts
                    title = title.lower()
                    
                    if title == 'example':
                        # Extract Swift code blocks
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
        # Clean up the documentation text
        doc_text = self._clean_description(doc_text)
        
        # Initialize the doc block
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
            'cases': []  # Add cases list for enum cases
        }
        
        # Split into sections by markdown headers
        sections = re.split(r'\n##\s+', doc_text)
        
        # Parse the main description (first section)
        main_section = sections[0].strip()
        
        # Split into description and tags
        parts = re.split(r'\n(?=(?:-\s+(?:' + '|'.join(self.tag_patterns.keys()) + r')\s*:))', main_section)
        if parts:
            # First part is the description
            description = parts[0].strip()
            doc_block['description'] = description
            
            # Remaining parts are tags
            if len(parts) > 1:
                tags_text = '\n'.join(parts[1:])
                self._parse_tags(tags_text, doc_block)
        
        # Process additional sections (Examples, etc.)
        for section in sections[1:]:
            if not section.strip():
                continue
            
            # Split section into title and content
            section_parts = section.split('\n', 1)
            if len(section_parts) < 2:
                continue
                
            title, content = section_parts
            title = title.lower()
            
            if title == 'example':
                # Extract Swift code blocks
                code_blocks = re.findall(r'```swift\n(.*?)```', content, re.DOTALL)
                if code_blocks:
                    doc_block['examples'] = [block.strip() for block in code_blocks]
            elif title == 'parameters':
                # Parse parameter list
                param_matches = self.parameter_pattern.finditer(content)
                for match in param_matches:
                    doc_block['parameters'].append({
                        'name': match.group(1),
                        'description': match.group(2).strip()
                    })
            elif title == 'cases':
                # Parse enum cases
                case_lines = content.strip().split('\n')
                for line in case_lines:
                    # Match lines starting with - `case_name`: description
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
        # Parse the actual tags
        for tag, pattern in self.tag_patterns.items():
            matches = re.finditer(pattern, tags_text, re.DOTALL)
            for match in matches:
                content = match.group(1).strip()
                if tag == 'Parameters':
                    # Parse individual parameters
                    param_matches = self.parameter_pattern.finditer(content)
                    for param_match in param_matches:
                        doc_block['parameters'].append({
                            'name': param_match.group(1),
                            'description': param_match.group(2).strip()
                        })
                elif tag == 'Case':
                    # Parse enum case
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
        # Check if this is a generic class first (special case)
        generic_class_match = re.search(r'(?:public\s+|private\s+|internal\s+|fileprivate\s+)?class\s+(\w+)\s*<', code_line)
        if generic_class_match:
            return 'type', generic_class_match.group(1)
        
        # Check other element types
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
        # Check if this is a multiline comment
        if text.startswith('/**'):
            # Remove /** and */ and * at beginning of lines
            text = re.sub(r'^\s*/\*\*\s*|\s*\*/\s*$', '', text)
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                # Remove * at beginning of lines
                line = re.sub(r'^\s*\*\s*', '', line)
                cleaned_lines.append(line.rstrip())
        else:
            # Remove /// and whitespace from the start of each line
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                # Remove comment markers and leading/trailing whitespace
                line = re.sub(r'^\s*///\s*', '', line)
                # Skip empty lines at the start
                if not cleaned_lines and not line.strip():
                    continue
                cleaned_lines.append(line.rstrip())
        
        # Join lines and clean up any trailing whitespace
        return '\n'.join(cleaned_lines).strip() 