"""Test script for the Kotlin parser."""

from thedoc.parsers.kotlin_parser import KotlinParser

def print_element_list(elements, indent=2):
    """Print a list of elements with their attributes."""
    for elem in elements:
        if 'name' in elem:
            print(f"{' ' * indent}- {elem['name']}: {elem['description']}")
        else:
            print(f"{' ' * indent}- {elem['text']}")

def main():
    """Run the parser on our sample file."""
    parser = KotlinParser()
    result = parser.parse_file("tests/kotlin/sample.kt")
    
    # Print the results in a readable format
    print("\nParsed Documentation:")
    print("=" * 50)
    
    # Print classes
    print("\nClasses:")
    for cls in result['classes']:
        print(f"\nClass: {cls['name']}")
        print(f"Description: {cls['description']}")
        if cls['properties']:
            print("Properties:")
            print_element_list(cls['properties'])
        if cls['see_also']:
            print("See Also:")
            print_element_list(cls['see_also'])
        if cls['samples']:
            print("Samples:")
            print_element_list(cls['samples'])
    
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
        if func['samples']:
            print("Samples:")
            print_element_list(func['samples'])
    
    # Print properties
    print("\nProperties:")
    for prop in result['properties']:
        print(f"\nProperty: {prop['name']}")
        print(f"Description: {prop['description']}")
        if prop['see_also']:
            print("See Also:")
            print_element_list(prop['see_also'])
    
    # Print enums
    print("\nEnums:")
    for enum in result['enums']:
        print(f"\nEnum: {enum['name']}")
        print(f"Description: {enum['description']}")
        if enum['properties']:
            print("Values:")
            print_element_list(enum['properties'])
    
    # Print types
    print("\nTypes:")
    for type_info in result['types']:
        print(f"\nType: {type_info['name']}")
        print(f"Description: {type_info['description']}")
        if type_info['parameters']:
            print("Type Parameters:")
            print_element_list(type_info['parameters'])
        if type_info['see_also']:
            print("See Also:")
            print_element_list(type_info['see_also'])

if __name__ == "__main__":
    main() 