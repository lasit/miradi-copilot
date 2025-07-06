"""
Check if diagram factors and links are being parsed.
"""

from src.etl.miradi_parser import MiradiParser

def check_diagram_data():
    """Check what diagram data is available."""
    
    print("=" * 60)
    print("DIAGRAM DATA CHECK")
    print("=" * 60)
    
    # Parse the file
    parser = MiradiParser()
    parsed_data = parser.parse_all("data/sample_projects/Bulgul_Rangers_v0.111.xmpz2")
    
    print(f"Parsed data keys: {list(parsed_data.keys())}")
    
    # Check if diagram factors and links are parsed
    diagram_factors = parsed_data.get('diagram_factors', [])
    diagram_links = parsed_data.get('diagram_links', [])
    
    print(f"\nDiagram factors found: {len(diagram_factors)}")
    print(f"Diagram links found: {len(diagram_links)}")
    
    if diagram_factors:
        first_factor = diagram_factors[0]
        print(f"\nFirst diagram factor ID: {first_factor.element_id}")
        print(f"Factor data keys: {list(first_factor.data.get('children', {}).keys())}")
        
        # Look for wrapped factor ID
        children = first_factor.data.get('children', {})
        wrapped_id = children.get('DiagramFactorWrappedFactorId', {}).get('text')
        print(f"Wrapped factor ID: {wrapped_id}")
    
    if diagram_links:
        first_link = diagram_links[0]
        print(f"\nFirst diagram link ID: {first_link.element_id}")
        print(f"Link data keys: {list(first_link.data.get('children', {}).keys())}")
        
        # Look for from/to factor IDs
        children = first_link.data.get('children', {})
        from_id = children.get('DiagramLinkFromDiagramFactorId', {}).get('text')
        to_id = children.get('DiagramLinkToDiagramFactorId', {}).get('text')
        print(f"From factor ID: {from_id}")
        print(f"To factor ID: {to_id}")
    
    # Check if the parser has methods to extract these
    print(f"\nParser methods:")
    methods = [method for method in dir(parser) if not method.startswith('_')]
    for method in methods:
        if 'diagram' in method.lower():
            print(f"  {method}")


if __name__ == "__main__":
    check_diagram_data()
