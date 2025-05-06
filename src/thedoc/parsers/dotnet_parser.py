"""Parser for .NET documentation comments."""

import re
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET
from pathlib import Path

class DotNetParser:
    """Parser for .NET documentation comments."""

    def __init__(self):
        """Initialize the parser."""
        # Pattern to match complete XML documentation blocks
        self.doc_block_pattern = re.compile(
            r'///\s*<(class|method|property|enum|interface|type)[^>]*>.*?</\1>',
            re.DOTALL
        )

    def parse_file(self, file_path: str) -> Dict:
        """Parse a .NET source file and extract documentation.

        Args:
            file_path: Path to the source file

        Returns:
            Dict containing parsed documentation
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Join all lines that start with /// to form complete blocks
        lines = content.split('\n')
        current_block = []
        doc_blocks = []
        
        for line in lines:
            if line.strip().startswith('///'):
                # Remove /// and leading/trailing whitespace
                clean_line = re.sub(r'^\s*///\s*', '', line)
                current_block.append(clean_line)
            elif current_block:
                # End of a documentation block
                doc_blocks.append('\n'.join(current_block))
                current_block = []
        
        if current_block:
            doc_blocks.append('\n'.join(current_block))
        
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
                # Parse the XML content
                root = ET.fromstring(block)
                
                # Process based on the root tag
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

    def _get_element_text(self, root: ET.Element, tag: str, default: str = '') -> str:
        """Get text content of an XML element.

        Args:
            root: Root XML element
            tag: Tag name to find
            default: Default value if tag not found

        Returns:
            Text content of the element or default value
        """
        elem = root.find(tag)
        if elem is None:
            return default
        
        # Handle special formatting tags
        text_parts = []
        for child in elem:
            if child.tag == 'para':
                text_parts.append(child.text.strip() if child.text else '')
            elif child.tag == 'c':
                text_parts.append(f"`{child.text}`" if child.text else '')
            elif child.tag == 'code':
                text_parts.append(f"```\n{child.text}\n```" if child.text else '')
            elif child.tag == 'list':
                text_parts.append(self._parse_list(child))
            elif child.tag == 'paramref':
                text_parts.append(f"`{child.get('name', '')}`")
            elif child.tag == 'typeparamref':
                text_parts.append(f"`{child.get('name', '')}`")
            elif child.tag == 'see':
                text_parts.append(self._parse_see_tag(child))
            elif child.tag == 'inheritdoc':
                text_parts.append("[Inherited documentation]")
            elif child.tag == 'include':
                text_parts.append(f"[Included from: {child.get('file', '')}]")
            else:
                text_parts.append(child.text.strip() if child.text else '')
        
        if not text_parts and elem.text:
            text_parts.append(elem.text.strip())
        
        return ' '.join(text_parts) if text_parts else default

    def _get_element_list(self, root: ET.Element, tag: str) -> List[Dict[str, Any]]:
        """Get list of elements with their attributes and content.

        Args:
            root: Root XML element
            tag: Tag name to find

        Returns:
            List of dictionaries containing element attributes and content
        """
        elements = []
        for elem in root.findall(tag):
            element_data = {
                'text': self._get_element_text(elem, '.'),
                'attributes': elem.attrib
            }
            elements.append(element_data)
        return elements

    def _parse_list(self, list_elem: ET.Element) -> str:
        """Parse a list element.

        Args:
            list_elem: List XML element

        Returns:
            Formatted list as string
        """
        list_type = list_elem.get('type', 'bullet')
        items = []
        for item in list_elem.findall('item'):
            term = item.find('term')
            description = item.find('description')
            if term is not None and description is not None:
                items.append(f"{term.text}: {description.text}")
            else:
                items.append(item.text.strip() if item.text else '')
        
        if list_type == 'number':
            return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))
        else:
            return '\n'.join(f"* {item}" for item in items)

    def _parse_see_tag(self, see_elem: ET.Element) -> str:
        """Parse a see tag.

        Args:
            see_elem: See XML element

        Returns:
            Formatted reference as string
        """
        cref = see_elem.get('cref', '')
        href = see_elem.get('href', '')
        text = see_elem.text.strip() if see_elem.text else ''
        
        if cref:
            return f"[{text or cref}]({cref})"
        elif href:
            return f"[{text or href}]({href})"
        return text

    def _parse_class(self, root: ET.Element) -> Dict:
        """Parse class documentation.

        Args:
            root: Root XML element

        Returns:
            Dict containing class documentation
        """
        return {
            'name': root.get('name', ''),
            'summary': self._get_element_text(root, 'summary'),
            'remarks': self._get_element_text(root, 'remarks'),
            'example': self._get_element_text(root, 'example'),
            'see_also': self._get_element_list(root, 'seealso'),
            'type_params': self._get_element_list(root, 'typeparam'),
            'inheritance': self._get_element_text(root, 'inheritdoc'),
            'includes': self._get_element_list(root, 'include')
        }

    def _parse_method(self, root: ET.Element) -> Dict:
        """Parse method documentation.

        Args:
            root: Root XML element

        Returns:
            Dict containing method documentation
        """
        return {
            'name': root.get('name', ''),
            'summary': self._get_element_text(root, 'summary'),
            'parameters': self._get_element_list(root, 'param'),
            'returns': self._get_element_text(root, 'returns'),
            'exceptions': self._get_element_list(root, 'exception'),
            'remarks': self._get_element_text(root, 'remarks'),
            'example': self._get_element_text(root, 'example'),
            'type_params': self._get_element_list(root, 'typeparam'),
            'see_also': self._get_element_list(root, 'seealso'),
            'inheritance': self._get_element_text(root, 'inheritdoc'),
            'includes': self._get_element_list(root, 'include')
        }

    def _parse_property(self, root: ET.Element) -> Dict:
        """Parse property documentation.

        Args:
            root: Root XML element

        Returns:
            Dict containing property documentation
        """
        return {
            'name': root.get('name', ''),
            'summary': self._get_element_text(root, 'summary'),
            'value': self._get_element_text(root, 'value'),
            'remarks': self._get_element_text(root, 'remarks'),
            'example': self._get_element_text(root, 'example'),
            'see_also': self._get_element_list(root, 'seealso'),
            'inheritance': self._get_element_text(root, 'inheritdoc'),
            'includes': self._get_element_list(root, 'include')
        }

    def _parse_enum(self, root: ET.Element) -> Dict:
        """Parse enum documentation.

        Args:
            root: Root XML element

        Returns:
            Dict containing enum documentation
        """
        return {
            'name': root.get('name', ''),
            'summary': self._get_element_text(root, 'summary'),
            'remarks': self._get_element_text(root, 'remarks'),
            'values': self._get_element_list(root, 'value'),
            'see_also': self._get_element_list(root, 'seealso'),
            'inheritance': self._get_element_text(root, 'inheritdoc'),
            'includes': self._get_element_list(root, 'include')
        }

    def _parse_interface(self, root: ET.Element) -> Dict:
        """Parse interface documentation.

        Args:
            root: Root XML element

        Returns:
            Dict containing interface documentation
        """
        return {
            'name': root.get('name', ''),
            'summary': self._get_element_text(root, 'summary'),
            'remarks': self._get_element_text(root, 'remarks'),
            'example': self._get_element_text(root, 'example'),
            'type_params': self._get_element_list(root, 'typeparam'),
            'see_also': self._get_element_list(root, 'seealso'),
            'inheritance': self._get_element_text(root, 'inheritdoc'),
            'includes': self._get_element_list(root, 'include')
        }

    def _parse_type(self, root: ET.Element) -> Dict:
        """Parse type documentation.

        Args:
            root: Root XML element

        Returns:
            Dict containing type documentation
        """
        return {
            'name': root.get('name', ''),
            'summary': self._get_element_text(root, 'summary'),
            'remarks': self._get_element_text(root, 'remarks'),
            'type_params': self._get_element_list(root, 'typeparam'),
            'see_also': self._get_element_list(root, 'seealso'),
            'inheritance': self._get_element_text(root, 'inheritdoc'),
            'includes': self._get_element_list(root, 'include')
        } 