"""Parser for Kotlin KDoc documentation."""

import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

class KotlinParser:
    """Parser for Kotlin KDoc documentation."""

    def __init__(self):
        """Initialize the parser."""
        # Pattern to match KDoc comments and the following code
        self.kdoc_pattern = re.compile(
            r'/\*\*(.*?)\*/\s*([^\n]*)',
            re.DOTALL
        )
        
        # Patterns for different KDoc tags
        self.tag_patterns = {
            'param': r'@param\s+(\w+)\s+(.*?)(?=@|\Z)',
            'return': r'@return\s+(.*?)(?=@|\Z)',
            'throws': r'@throws\s+(\w+)\s+(.*?)(?=@|\Z)',
            'property': r'@property\s+(\w+)\s+(.*?)(?=@|\Z)',
            'see': r'@see\s+(.*?)(?=@|\Z)',
            'sample': r'@sample\s+(.*?)(?=@|\Z)',
        }
        
        # Patterns for Kotlin code elements
        self.code_patterns = {
            'class': re.compile(r'class\s+(\w+)(?!\s*<)'),  # Don't match generic classes
            'function': re.compile(r'fun\s+(\w+)'),
            'property': re.compile(r'(var|val)\s+(\w+)'),
            'enum': re.compile(r'enum\s+class\s+(\w+)'),
            'type': re.compile(r'class\s+(\w+)\s*<\s*(\w+)\s*>')  # Match generic classes
        }
        
        # Mapping of element types to their plural forms
        self.plural_map = {
            'class': 'classes',
            'function': 'functions',
            'property': 'properties',
            'enum': 'enums',
            'type': 'types'
        }

    def parse_file(self, file_path: str) -> Dict:
        """Parse a Kotlin source file and extract documentation.

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
            'types': []
        }

        # Find all KDoc comments and their following code
        for match in self.kdoc_pattern.finditer(content):
            kdoc = match.group(1).strip()
            code_line = match.group(2).strip()
            
            # Extract the main description (text before any @tags)
            description = self._clean_description(kdoc.split('@')[0].strip())
            
            # Parse the documentation block
            doc_block = {
                'description': description,
                'parameters': self._parse_tag(kdoc, 'param'),
                'returns': self._parse_tag(kdoc, 'return'),
                'throws': self._parse_tag(kdoc, 'throws'),
                'properties': self._parse_tag(kdoc, 'property'),
                'see_also': self._parse_tag(kdoc, 'see'),
                'samples': self._parse_tag(kdoc, 'sample')
            }

            # Determine the type of code element and add name
            element_type, name = self._detect_code_element(code_line)
            if element_type and name:
                doc_block['name'] = name
                plural_type = self.plural_map[element_type]
                documentation[plural_type].append(doc_block)

        return documentation

    def _detect_code_element(self, code_line: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect the type of Kotlin code element and its name.

        Args:
            code_line: The line of code following the KDoc comment

        Returns:
            Tuple of (element_type, element_name) or (None, None) if not detected
        """
        for element_type, pattern in self.code_patterns.items():
            match = pattern.search(code_line)
            if match:
                if element_type == 'property':
                    return element_type, match.group(2)  # Group 2 contains the property name
                return element_type, match.group(1)
        return None, None

    def _clean_description(self, text: str) -> str:
        """Clean up the description text by removing asterisks and extra whitespace.

        Args:
            text: The description text to clean

        Returns:
            Cleaned description text
        """
        # Remove leading/trailing asterisks and whitespace
        text = re.sub(r'^\s*\*\s*', '', text)
        text = re.sub(r'\s*\*\s*$', '', text)
        
        # Remove asterisks from the start of each line
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'^\s*\*\s*', '', line)
            if line.strip():
                cleaned_lines.append(line.strip())
        
        return '\n'.join(cleaned_lines)

    def _parse_tag(self, kdoc: str, tag: str) -> List[Dict[str, str]]:
        """Parse a specific KDoc tag.

        Args:
            kdoc: The KDoc comment text
            tag: The tag to parse

        Returns:
            List of dictionaries containing tag information
        """
        if tag not in self.tag_patterns:
            return []

        pattern = self.tag_patterns[tag]
        matches = re.finditer(pattern, kdoc, re.DOTALL)
        
        results = []
        for match in matches:
            if tag in ['param', 'throws', 'property']:
                name = match.group(1)
                description = self._clean_description(match.group(2))
                results.append({
                    'name': name,
                    'description': description
                })
            else:
                text = self._clean_description(match.group(1))
                results.append({
                    'text': text
                })
        
        return results 