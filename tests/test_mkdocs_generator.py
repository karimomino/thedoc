"""Tests for the MkDocs generator."""

import os
import shutil
import tempfile
from pathlib import Path
import pytest

from thedoc.mkdocs_generator import MkDocsGenerator
from thedoc.config import DEFAULT_CONFIG

class TestMkDocsGenerator:
    """Tests for the MkDocs generator."""
    
    @pytest.fixture
    def setup_test_project(self):
        """Setup a test project with sample files."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        try:
            # Create a test project structure
            project_path = Path(temp_dir)
            
            # Create a Python file with docstrings
            py_dir = project_path / "src" / "sample"
            py_dir.mkdir(parents=True)
            
            py_file = py_dir / "sample.py"
            py_file.write_text('''"""Sample module docstring."""

class SampleClass:
    """A sample class for testing.
    
    This class demonstrates how docstrings are parsed.
    """
    
    def sample_method(self, param1, param2):
        """Sample method with parameters.
        
        Args:
            param1: The first parameter.
            param2: The second parameter.
            
        Returns:
            A sample return value.
        """
        return param1 + param2
''')
            
            # Create a Swift file with documentation comments
            swift_dir = project_path / "Sources"
            swift_dir.mkdir(parents=True)
            
            swift_file = swift_dir / "Sample.swift"
            swift_file.write_text('''/// A sample Swift class.
/// This class demonstrates how Swift documentation is parsed.
public class SampleSwift {
    
    /// A sample property with documentation.
    var sampleProperty: String
    
    /// Creates a new instance of SampleSwift.
    /// - Parameters:
    ///   - value: The initial value for the property.
    public init(value: String) {
        self.sampleProperty = value
    }
    
    /// A sample method with parameters and return value.
    /// - Parameters:
    ///   - param1: The first parameter.
    ///   - param2: The second parameter.
    /// - Returns: The combined result of the parameters.
    public func sampleMethod(param1: String, param2: String) -> String {
        return param1 + param2
    }
}
''')
            
            yield project_path
        finally:
            # Clean up
            shutil.rmtree(temp_dir)
    
    def test_detect_project_languages(self, setup_test_project, monkeypatch):
        """Test language detection."""
        project_path = setup_test_project
        
        # Mock config loading
        def mock_load_config():
            return DEFAULT_CONFIG.copy()
        
        monkeypatch.setattr("thedoc.config.load_config", mock_load_config)
        
        # Create generator
        generator = MkDocsGenerator(project_path)
        
        # Detect languages
        detected = generator.detect_project_languages()
        
        # Check results
        assert "Python" in detected
        assert "Swift" in detected
    
    def test_generate_markdown(self, setup_test_project, monkeypatch):
        """Test markdown generation."""
        project_path = setup_test_project
        
        # Mock config loading
        def mock_load_config():
            config = DEFAULT_CONFIG.copy()
            config["project_name"] = "Test Project"
            return config
        
        monkeypatch.setattr("thedoc.config.load_config", mock_load_config)
        
        # Create generator
        generator = MkDocsGenerator(project_path)
        
        # Generate documentation
        generator.generate()
        
        # Check that docs directory was created
        docs_dir = project_path / "docs"
        assert docs_dir.exists()
        
        # Check that mkdocs.yml was created
        mkdocs_config = docs_dir / "mkdocs.yml"
        assert mkdocs_config.exists()
        
        # Check that markdown files were created
        docs_docs_dir = docs_dir / "docs"
        assert docs_docs_dir.exists()
        
        # Check index.md
        index = docs_docs_dir / "index.md"
        assert index.exists()
        assert "Test Project" in index.read_text()
        
        # Check that language directories were created
        python_dir = docs_docs_dir / "python"
        swift_dir = docs_docs_dir / "swift"
        
        assert python_dir.exists()
        assert swift_dir.exists() 