"""Tests for the .NET parser."""

import os
from pathlib import Path
import pytest
from thedoc.parsers.dotnet_parser import DotNetParser

@pytest.fixture
def parser():
    """Create a parser instance."""
    return DotNetParser()

@pytest.fixture
def sample_cs_file(tmp_path):
    """Create a sample C# file for testing."""
    file_path = tmp_path / "calculator.cs"
    with open(file_path, "w") as f:
        f.write("""
/// <class name="Calculator">
/// <summary>
/// Performs basic arithmetic operations.
/// </summary>
/// <remarks>
/// This class is thread-safe.
/// </remarks>
/// <example>
/// var calc = new Calculator();
/// var result = calc.Add(2, 3);
/// </example>
/// </class>
public class Calculator
{
    /// <method name="Add">
    /// <summary>
    /// Adds two numbers.
    /// </summary>
    /// <param name="a">First number</param>
    /// <param name="b">Second number</param>
    /// <returns>The sum of the two numbers.</returns>
    /// </method>
    public int Add(int a, int b)
    {
        return a + b;
    }
}
""")
    return file_path

def test_parse_file(parser, sample_cs_file):
    """Test parsing a C# file with documentation comments."""
    result = parser.parse_file(str(sample_cs_file))

    # Check classes
    assert len(result['classes']) == 1
    calculator_class = result['classes'][0]
    assert calculator_class['name'] == 'Calculator'
    assert 'Performs basic arithmetic operations' in calculator_class['summary']
    assert 'This class is thread-safe' in calculator_class['remarks']
    assert 'var calc = new Calculator()' in calculator_class['example']

    # Check methods
    assert len(result['methods']) == 1
    add_method = result['methods'][0]
    assert add_method['name'] == 'Add'
    assert 'Adds two numbers' in add_method['summary']
    assert len(add_method['parameters']) == 2
    assert add_method['parameters'][0]['attributes']['name'] == 'a'
    assert 'First number' in add_method['parameters'][0]['text']
    assert 'sum of the two numbers' in add_method['returns']

def test_parse_file_with_invalid_xml(parser, tmp_path):
    """Test parsing a file with invalid XML documentation."""
    file_path = tmp_path / "invalid.cs"
    with open(file_path, "w") as f:
        f.write("""
/// <class name="Invalid">
/// <summary>
/// This has invalid XML.
/// <unclosed>
/// </summary>
/// </class>
public class Invalid {}
""")
    
    result = parser.parse_file(str(file_path))
    assert result['classes'] == []  # Should gracefully handle invalid XML

def test_parse_file_with_no_documentation(parser, tmp_path):
    """Test parsing a file with no documentation."""
    file_path = tmp_path / "nodocs.cs"
    with open(file_path, "w") as f:
        f.write("""
public class NoDocumentation
{
    public void UndocumentedMethod() {}
}
""")
    
    result = parser.parse_file(str(file_path))
    assert result['classes'] == []
    assert result['methods'] == []

def test_parse_comprehensive_sample(parser):
    """Test parsing the comprehensive sample.cs file in the tests/dotnet directory."""
    sample_path = os.path.join("tests", "dotnet", "sample.cs")
    result = parser.parse_file(sample_path)
    
    # Check classes
    assert len(result['classes']) == 1
    math_class = result['classes'][0]
    assert math_class['name'] == 'MathOperations'
    assert 'mathematical operations' in math_class['summary']
    assert 'thread-safe' in math_class['remarks']
    
    # Check methods
    assert len(result['methods']) == 1
    multiply_method = result['methods'][0]
    assert multiply_method['name'] == 'Multiply'
    assert 'Multiplies two numbers' in multiply_method['summary']
    assert len(multiply_method['parameters']) == 2
    assert 'first number' in multiply_method['parameters'][0]['text'].lower()
    assert 'product of the two numbers' in multiply_method['returns']
    assert len(multiply_method['exceptions']) == 1
    assert 'ArgumentException' in multiply_method['exceptions'][0]['attributes']['cref']
    
    # Check properties
    assert len(result['properties']) == 1
    last_result_prop = result['properties'][0]
    assert last_result_prop['name'] == 'LastResult'
    assert 'Gets the result' in last_result_prop['summary']
    assert 'last calculated result' in last_result_prop['value']
    
    # Check enums
    assert len(result['enums']) == 1
    op_type_enum = result['enums'][0]
    assert op_type_enum['name'] == 'OperationType'
    assert 'types of operations' in op_type_enum['summary']
    
    # Check types/generics
    assert len(result['types']) == 1
    type_param = result['types'][0]
    assert type_param['name'] == 'T'
    assert 'generic type parameter' in type_param['summary'].lower()
    assert len(type_param['type_params']) == 1
    assert type_param['type_params'][0]['attributes']['name'] == 'T' 