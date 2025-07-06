"""
Debug the diagram factor and link data structure.
"""

from src.etl.miradi_parser import MiradiParser

def debug_diagram_structure():
    """Debug diagram factor and link data structure."""
    
    print("=" * 60)
    print("DIAGRAM STRUCTURE DEBUG")
    print("=" * 60)
    
    # Parse the file
    parser = MiradiParser()
    parsed_data = parser.parse_all("data/sample_projects/Bulgul_Rangers_v0.111.xmpz2")
    
    # Look at first diagram factor in detail
    diagram_factors = parsed_data.get('diagram_factors', [])
    if diagram_factors:
        first_factor = diagram_factors[0]
        print(f"First diagram factor ID: {first_factor.element_id}")
        print(f"Factor data keys: {list(first_factor.data.get('children', {}).keys())}")
        
        # Print the full data structure
        children = first_factor.data.get('children', {})
        for key, value in children.items():
            print(f"\n{key}: {value}")
    
    # Look at first diagram link in detail
    diagram_links = parsed_data.get('diagram_links', [])
    if diagram_links:
        first_link = diagram_links[0]
        print(f"\nFirst diagram link ID: {first_link.element_id}")
        print(f"Link data keys: {list(first_link.data.get('children', {}).keys())}")
        
        # Print the full data structure
        children = first_link.data.get('children', {})
        for key, value in children.items():
            print(f"\n{key}: {value}")


if __name__ == "__main__":
    debug_diagram_structure()
