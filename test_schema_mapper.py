"""
Test script for the schema mapper to verify relationship creation.

This script tests the MiradiToGraphMapper to ensure it correctly creates
conservation relationships between elements.
"""

import logging
from src.etl.miradi_parser import MiradiParser
from src.etl.schema_mapper import MiradiToGraphMapper

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_schema_mapper():
    """Test the schema mapper with relationship creation."""
    
    print("=" * 60)
    print("SCHEMA MAPPER RELATIONSHIP TEST")
    print("=" * 60)
    
    # Parse the file
    print("Initializing parser...")
    parser = MiradiParser()
    
    print("Parsing Bulgul Rangers project...")
    parsed_data = parser.parse_all("data/sample_projects/Bulgul_Rangers_v0.111.xmpz2")
    
    print(f"Parsed data keys: {list(parsed_data.keys())}")
    print(f"Conservation targets: {len(parsed_data.get('conservation_targets', []))}")
    print(f"Threats: {len(parsed_data.get('threats', []))}")
    print(f"Strategies: {len(parsed_data.get('strategies', []))}")
    print(f"Activities: {len(parsed_data.get('activities', []))}")
    
    # Test schema mapper
    print("\n" + "=" * 60)
    print("TESTING SCHEMA MAPPER")
    print("=" * 60)
    
    mapper = MiradiToGraphMapper()
    result = mapper.map_project_to_graph(parsed_data)
    
    print(f"\nConversion Results:")
    print(f"Total nodes created: {len(result.nodes)}")
    print(f"Total relationships created: {len(result.relationships)}")
    
    # Analyze relationship types
    relationship_counts = {}
    for rel in result.relationships:
        rel_type = rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else str(rel.relationship_type)
        relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
    
    print(f"\nRelationship breakdown:")
    for rel_type, count in relationship_counts.items():
        print(f"  {rel_type}: {count}")
    
    # Show some example relationships
    print(f"\nExample relationships:")
    for i, rel in enumerate(result.relationships[:10]):  # Show first 10
        rel_type = rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else str(rel.relationship_type)
        print(f"  {i+1}. {rel.source_id} --{rel_type}--> {rel.target_id}")
    
    # Check for errors
    if result.errors:
        print(f"\nErrors encountered:")
        for error in result.errors:
            print(f"  - {error}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_schema_mapper()
