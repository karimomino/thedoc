"""MkDocs generator for TheDoc.

This module handles the generation of MkDocs documentation from extracted code documentation.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil

from .parsers import BaseParser, DocItem, PythonParser, SwiftParser, KotlinParser, DotNetParser
from .config import load_config

class MkDocsGenerator:
    """Generates MkDocs documentation from extracted code documentation."""
    
    def __init__(self, project_path: Path):
        """Initialize the MkDocs generator.
        
        Args:
            project_path: Path to the project root
        """
        self.project_path = project_path
        self.config = load_config()
        self.docs_dir = project_path / self.config["output_dir"]
        self.mkdocs_dir = self.docs_dir / "docs"
        self.mkdocs_config_file = self.docs_dir / "mkdocs.yml"
        
        self.parser_map = {
            '.py': PythonParser(project_path),
            '.swift': SwiftParser(project_path),
            '.kt': KotlinParser(project_path),
            '.kts': KotlinParser(project_path),
            '.cs': DotNetParser(project_path),
            '.vb': DotNetParser(project_path),
        }
        
        self.plural_map = {
            'class': 'Classes',
            'function': 'Functions',
            'method': 'Methods',
            'property': 'Properties',
            'module': 'Modules',
            'enum': 'Enumerations',
            'interface': 'Interfaces',
            'case': 'Cases',
            'type': 'Types',
            'object': 'Objects',
            'unknown': 'Miscellaneous'
        }
        
        self.detected_languages = set()
        
    def detect_project_languages(self) -> List[str]:
        """Detect programming languages used in the project.
        
        Returns:
            List of detected programming languages
        """
        language_extensions = {
            '.py': 'Python',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.kts': 'Kotlin',
            '.java': 'Java',
            '.cs': 'C#',
            '.vb': 'Visual Basic',
            '.go': 'Go',
            '.rs': 'Rust',
            '.js': 'JavaScript',
            '.ts': 'TypeScript'
        }
        
        detected = set()
        
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in language_extensions:
                detected.add(language_extensions[file_path.suffix])
                self.detected_languages.add(file_path.suffix)
        
        return list(detected)
    
    def extract_documentation(self) -> Dict[str, List[DocItem]]:
        """Extract documentation from all supported files in the project.
        
        Returns:
            Dictionary containing all extracted documentation grouped by language
        """
        all_docs = {}
        
        for ext in self.detected_languages:
            if ext in self.parser_map:
                parser = self.parser_map[ext]
                lang_name = next((l for e, l in {
                    '.py': 'Python', 
                    '.swift': 'Swift', 
                    '.kt': 'Kotlin',
                    '.kts': 'Kotlin',
                    '.cs': 'C#',
                    '.vb': 'Visual Basic'
                }.items() if e == ext), ext)
                
                print(f"Extracting documentation for {lang_name} files...")
                
                files = [f for f in self.project_path.rglob(f"*{ext}") 
                         if not any(pattern in str(f) for pattern in self.config["exclude_patterns"])]
                
                file_docs = {}
                for file_path in files:
                    try:
                        relative_path = file_path.relative_to(self.project_path)
                        doc_items = parser.parse_file(file_path)
                        if doc_items:
                            file_docs[str(relative_path)] = doc_items
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
                
                if file_docs:
                    all_docs[lang_name] = file_docs
        
        return all_docs
    
    def generate_markdown(self, documentation: Dict[str, Dict[str, List[DocItem]]]) -> None:
        """Generate Markdown files from extracted documentation.
        
        Args:
            documentation: Dictionary containing all extracted documentation
        """
        self.mkdocs_dir.mkdir(parents=True, exist_ok=True)
        
        self._create_index_file()
        
        for language, files in documentation.items():
            lang_dir = self.mkdocs_dir / language.lower().replace('#', 'sharp').replace('+', 'plus')
            lang_dir.mkdir(exist_ok=True)
            
            self._create_language_index(language, lang_dir, files)
            
            for file_path, doc_items in files.items():
                self._create_file_documentation(language, file_path, doc_items, lang_dir)
    
    def _create_index_file(self) -> None:
        """Create the main index.md file for the documentation."""
        index_content = f"""# {self.config['project_name'] or 'Project'} Documentation

This documentation was automatically generated by TheDoc.

## Project Overview

This project contains code in the following languages:

{chr(10).join(['* ' + lang for lang in self.detect_project_languages()])}

## Documentation Structure

The documentation is organized by programming language. Each language section contains
documentation for all files with documentation comments.

"""
        with open(self.mkdocs_dir / "index.md", "w") as f:
            f.write(index_content)
    
    def _create_language_index(self, language: str, lang_dir: Path, files: Dict[str, List[DocItem]]) -> None:
        """Create the index.md file for a specific language.
        
        Args:
            language: The programming language
            lang_dir: The directory for the language documentation
            files: Dictionary of files with their documentation items
        """
        index_content = f"""# {language} Documentation

This section contains documentation for {language} code in the project.

## Files

"""
        for file_path in sorted(files.keys()):
            safe_filename = file_path.replace("/", "_").replace("\\", "_")
            index_content += f"* [{file_path}]({safe_filename}.md)\n"
        
        with open(lang_dir / "index.md", "w") as f:
            f.write(index_content)
    
    def _create_file_documentation(self, language: str, file_path: str, 
                                 doc_items: List[DocItem], lang_dir: Path) -> None:
        """Create Markdown documentation for a specific file.
        
        Args:
            language: The programming language
            file_path: The path to the source file
            doc_items: List of documentation items for the file
            lang_dir: The directory for the language documentation
        """
        safe_filename = file_path.replace("/", "_").replace("\\", "_")
        md_file = lang_dir / f"{safe_filename}.md"
        
        with open(md_file, "w") as f:
            f.write(f"# {os.path.basename(file_path)}\n\n")
            f.write(f"**Path:** `{file_path}`\n\n")
            
            items_by_type = {}
            for item in doc_items:
                if item.type not in items_by_type:
                    items_by_type[item.type] = []
                items_by_type[item.type].append(item)
            
            for item_type, items in sorted(items_by_type.items()):
                if items:
                    section_title = self.plural_map.get(item_type, f"{item_type.capitalize()}s")
                    f.write(f"## {section_title}\n\n")
                    
                    for item in items:
                        f.write(f"### {item.name}\n\n")
                        
                        if item.description:
                            f.write(f"{item.description}\n\n")
                        
                        if item.signature:
                            f.write("```%s\n%s\n```\n\n" % (language.lower().replace('#', 'csharp').replace('+', 'cpp'), item.signature))
                        
                        if item.params:
                            f.write("**Parameters:**\n\n")
                            for param_name, param_desc in item.params.items():
                                f.write(f"* `{param_name}`: {param_desc}\n")
                            f.write("\n")
                        
                        if item.returns:
                            f.write(f"**Returns:** {item.returns}\n\n")
                        
                        if item.examples:
                            f.write("**Examples:**\n\n")
                            for example in item.examples:
                                f.write("```%s\n%s\n```\n\n" % (language.lower().replace('#', 'csharp').replace('+', 'cpp'), example))
                        
                        f.write("---\n\n")
    
    def create_mkdocs_config(self) -> None:
        """Create the MkDocs configuration file."""
        config = {
            "site_name": self.config['project_name'] or "Project Documentation",
            "theme": {
                "name": "material",
                "palette": {
                    "primary": "indigo",
                    "accent": "indigo"
                },
                "features": [
                    "navigation.tabs",
                    "navigation.sections",
                    "toc.integrate"
                ]
            },
            "markdown_extensions": [
                "pymdownx.highlight",
                "pymdownx.superfences",
                "admonition",
                "toc"
            ],
            "nav": [
                {"Home": "index.md"}
            ]
        }
        
        for language in self.detect_project_languages():
            lang_path = language.lower().replace('#', 'sharp').replace('+', 'plus')
            config["nav"].append({language: f"{lang_path}/index.md"})
        
        with open(self.mkdocs_config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def generate(self) -> None:
        """Generate the MkDocs documentation."""
        print("Detecting programming languages in the project...")
        detected = self.detect_project_languages()
        print(f"Detected languages: {', '.join(detected)}")
        
        print("Extracting documentation...")
        documentation = self.extract_documentation()
        
        if self.mkdocs_dir.exists():
            shutil.rmtree(self.mkdocs_dir)
        
        print("Generating Markdown files...")
        self.generate_markdown(documentation)
        
        print("Creating MkDocs configuration...")
        self.create_mkdocs_config()
        
        print(f"Documentation generated successfully in {self.docs_dir}")
        print("Run 'cd docs && mkdocs serve' to view the documentation") 