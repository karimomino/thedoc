"""Test script for the .NET parser."""

from thedoc.parsers.dotnet_parser import DotNetParser
import json

def print_element_list(elements, indent=2):
    """Print a list of elements with their attributes."""
    for elem in elements:
        print(f"{' ' * indent}- Text: {elem['text']}")
        if elem['attributes']:
            print(f"{' ' * (indent + 2)}Attributes: {elem['attributes']}")

def main():
    """Run the parser on our sample file."""
    parser = DotNetParser()
    result = parser.parse_file("tests/dotnet/sample.cs")
    
    # Print the results in a readable format
    print("\nParsed Documentation:")
    print("=" * 50)
    
    # Print classes
    print("\nClasses:")
    for cls in result['classes']:
        print(f"\nClass: {cls['name']}")
        print(f"Summary: {cls['summary']}")
        print(f"Remarks: {cls['remarks']}")
        print(f"Example: {cls['example']}")
        if cls['see_also']:
            print("See Also:")
            print_element_list(cls['see_also'])
        if cls['type_params']:
            print("Type Parameters:")
            print_element_list(cls['type_params'])
        if cls['inheritance']:
            print(f"Inheritance: {cls['inheritance']}")
        if cls['includes']:
            print("Includes:")
            print_element_list(cls['includes'])
    
    # Print methods
    print("\nMethods:")
    for method in result['methods']:
        print(f"\nMethod: {method['name']}")
        print(f"Summary: {method['summary']}")
        print("Parameters:")
        print_element_list(method['parameters'])
        print(f"Returns: {method['returns']}")
        print("Exceptions:")
        print_element_list(method['exceptions'])
        print(f"Remarks: {method['remarks']}")
        print(f"Example: {method['example']}")
        if method['type_params']:
            print("Type Parameters:")
            print_element_list(method['type_params'])
        if method['see_also']:
            print("See Also:")
            print_element_list(method['see_also'])
        if method['inheritance']:
            print(f"Inheritance: {method['inheritance']}")
        if method['includes']:
            print("Includes:")
            print_element_list(method['includes'])
    
    # Print properties
    print("\nProperties:")
    for prop in result['properties']:
        print(f"\nProperty: {prop['name']}")
        print(f"Summary: {prop['summary']}")
        print(f"Value: {prop['value']}")
        print(f"Remarks: {prop['remarks']}")
        print(f"Example: {prop['example']}")
        if prop['see_also']:
            print("See Also:")
            print_element_list(prop['see_also'])
        if prop['inheritance']:
            print(f"Inheritance: {prop['inheritance']}")
        if prop['includes']:
            print("Includes:")
            print_element_list(prop['includes'])
    
    # Print enums
    print("\nEnums:")
    for enum in result['enums']:
        print(f"\nEnum: {enum['name']}")
        print(f"Summary: {enum['summary']}")
        print(f"Remarks: {enum['remarks']}")
        print("Values:")
        print_element_list(enum['values'])
        if enum['see_also']:
            print("See Also:")
            print_element_list(enum['see_also'])
        if enum['inheritance']:
            print(f"Inheritance: {enum['inheritance']}")
        if enum['includes']:
            print("Includes:")
            print_element_list(enum['includes'])
    
    # Print types
    print("\nTypes:")
    for type_info in result['types']:
        print(f"\nType: {type_info['name']}")
        print(f"Summary: {type_info['summary']}")
        print(f"Remarks: {type_info['remarks']}")
        if type_info['type_params']:
            print("Type Parameters:")
            print_element_list(type_info['type_params'])
        if type_info['see_also']:
            print("See Also:")
            print_element_list(type_info['see_also'])
        if type_info['inheritance']:
            print(f"Inheritance: {type_info['inheritance']}")
        if type_info['includes']:
            print("Includes:")
            print_element_list(type_info['includes'])

if __name__ == "__main__":
    main() 