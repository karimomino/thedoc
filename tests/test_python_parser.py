"""Tests for the Python parser."""

from pathlib import Path
import textwrap
from thedoc.parsers import PythonParser

def test_parse_function():
    """Test parsing a Python function with docstring."""
    code = textwrap.dedent('''
        def hello(name: str, age: int = None) -> str:
            """Say hello to someone.
            
            Args:
                name: The name of the person
                age: Optional age of the person
                
            Returns:
                A greeting message
                
            Example:
                >>> hello("Alice", 25)
                'Hello Alice, you are 25 years old!'
            """
            if age is not None:
                return f"Hello {name}, you are {age} years old!"
            return f"Hello {name}!"
    ''')
    
    # Create a temporary file
    tmp_file = Path('test_func.py')
    try:
        tmp_file.write_text(code)
        
        parser = PythonParser(Path('.'))
        items = parser.parse_file(tmp_file)
        
        assert len(items) == 1
        item = items[0]
        
        assert item.name == 'hello'
        assert item.type == 'function'
        assert 'Say hello to someone' in item.description
        assert item.signature == 'hello(name, age)'
        assert len(item.params) == 2
        assert 'name' in item.params
        assert 'age' in item.params
        assert item.returns is not None
        assert len(item.examples) == 1
    finally:
        tmp_file.unlink()

def test_parse_class():
    """Test parsing a Python class with methods."""
    code = textwrap.dedent('''
        class Person:
            """A class representing a person.
            
            This class stores basic information about a person.
            """
            
            def __init__(self, name: str):
                """Initialize a person.
                
                Args:
                    name: The person's name
                """
                self.name = name
                
            def greet(self) -> str:
                """Generate a greeting.
                
                Returns:
                    A greeting message
                """
                return f"Hello, I'm {self.name}!"
    ''')
    
    # Create a temporary file
    tmp_file = Path('test_class.py')
    try:
        tmp_file.write_text(code)
        
        parser = PythonParser(Path('.'))
        items = parser.parse_file(tmp_file)
        
        assert len(items) == 3  # Class + 2 methods
        
        # Check class
        class_item = next(item for item in items if item.type == 'class')
        assert class_item.name == 'Person'
        assert 'representing a person' in class_item.description
        
        # Check methods
        init_method = next(item for item in items if item.name == 'Person.__init__')
        assert init_method.type == 'method'
        assert len(init_method.params) == 1
        assert 'name' in init_method.params
        
        greet_method = next(item for item in items if item.name == 'Person.greet')
        assert greet_method.type == 'method'
        assert greet_method.returns is not None
    finally:
        tmp_file.unlink()

def test_parse_module():
    """Test parsing a Python module with docstring."""
    code = textwrap.dedent('''
        """A test module.
        
        This module contains test code.
        """
        
        def func():
            pass
    ''')
    
    # Create a temporary file
    tmp_file = Path('test_module.py')
    try:
        tmp_file.write_text(code)
        
        parser = PythonParser(Path('.'))
        items = parser.parse_file(tmp_file)
        
        assert len(items) == 1
        assert items[0].type == 'module'
        assert items[0].name == 'test_module'
        assert 'test module' in items[0].description.lower()
    finally:
        tmp_file.unlink() 