"""Test script for the Swift parser."""

from thedoc.parsers.swift_parser import SwiftParser

def print_element_list(elements, indent=2):
    """Print a list of elements with their attributes."""
    for elem in elements:
        if 'name' in elem:
            print(f"{' ' * indent}- {elem['name']}: {elem['description']}")
        else:
            print(f"{' ' * indent}- {elem['text']}")

def main():
    """Run the parser on our sample file."""
    parser = SwiftParser()
    result = parser.parse_file("tests/swift/sample.swift")
    
    # Print the results in a readable format
    print("\nParsed Documentation:")
    print("=" * 50)
    
    # Print classes
    print("\nClasses:")
    for cls in result['classes']:
        print(f"\nClass: {cls['name']}")
        print(f"Description: {cls['description']}")
        if cls.get('examples'):
            print("Examples:")
            for example in cls['examples']:
                print(f"{' ' * 2}- ```swift\n{example}\n  ```")
        if cls['notes']:
            print("Notes:")
            print_element_list(cls['notes'])
        if cls['warnings']:
            print("Warnings:")
            print_element_list(cls['warnings'])
        if cls['see_also']:
            print("See Also:")
            print_element_list(cls['see_also'])
    
    # Print functions
    print("\nFunctions:")
    for func in result['functions']:
        print(f"\nFunction: {func['name']}")
        print(f"Description: {func['description']}")
        if func['parameters']:
            print("Parameters:")
            print_element_list(func['parameters'])
        if func['returns']:
            print("Returns:")
            print_element_list(func['returns'])
        if func['throws']:
            print("Throws:")
            print_element_list(func['throws'])
        if func.get('examples'):
            print("Examples:")
            for example in func['examples']:
                print(f"{' ' * 2}- ```swift\n{example}\n  ```")
        if func['preconditions']:
            print("Preconditions:")
            print_element_list(func['preconditions'])
        if func['postconditions']:
            print("Postconditions:")
            print_element_list(func['postconditions'])
    
    # Print properties
    print("\nProperties:")
    for prop in result['properties']:
        print(f"\nProperty: {prop['name']}")
        print(f"Description: {prop['description']}")
        if prop['important']:
            print("Important:")
            print_element_list(prop['important'])
    
    # Print enums
    print("\nEnums:")
    for enum in result['enums']:
        print(f"\nEnum: {enum['name']}")
        print(f"Description: {enum['description']}")
    
    # Print enum cases
    print("\nEnum Cases:")
    for case in result['cases']:
        print(f"\nCase: {case['name']}")
        print(f"Description: {case['description']}")
    
    # Print types
    print("\nTypes:")
    for type_info in result['types']:
        print(f"\nType: {type_info['name']}")
        print(f"Description: {type_info['description']}")
        if type_info.get('examples'):
            print("Examples:")
            for example in type_info['examples']:
                print(f"{' ' * 2}- ```swift\n{example}\n  ```")
        if type_info['notes']:
            print("Notes:")
            print_element_list(type_info['notes'])

if __name__ == "__main__":
    main() 