"""
Script to inspect the raw data structure to find relationship patterns.
"""

from src.etl.miradi_parser import MiradiParser
import json

def inspect_relationships():
    """Inspect the raw data to find relationship patterns."""
    
    print("=" * 60)
    print("RELATIONSHIP DATA INSPECTION")
    print("=" * 60)
    
    # Parse the file
    parser = MiradiParser()
    parsed_data = parser.parse_all("data/sample_projects/Bulgul_Rangers_v0.111.xmpz2")
    
    # Look at first strategy in detail
    strategies = parsed_data.get('strategies', [])
    if strategies:
        first_strategy = strategies[0]
        print(f"First strategy ID: {first_strategy.element_id}")
        print(f"First strategy name: {first_strategy.name}")
        print(f"Strategy data keys: {list(first_strategy.data.get('children', {}).keys())}")
        
        # Look for activity references
        children = first_strategy.data.get('children', {})
        for key, value in children.items():
            if 'activity' in key.lower() or 'task' in key.lower():
                print(f"\nFound activity-related field: {key}")
                print(f"Value: {value}")
    
    # Look at first threat in detail
    threats = parsed_data.get('threats', [])
    if threats:
        first_threat = threats[0]
        print(f"\nFirst threat ID: {first_threat.element_id}")
        print(f"First threat name: {first_threat.name}")
        print(f"Threat data keys: {list(first_threat.data.get('children', {}).keys())}")
        
        # Look for target references
        children = first_threat.data.get('children', {})
        for key, value in children.items():
            if 'target' in key.lower() or 'biodiversity' in key.lower():
                print(f"\nFound target-related field: {key}")
                print(f"Value: {value}")
    
    # Look for any link objects in the parsed data
    print(f"\nAll parsed data keys: {list(parsed_data.keys())}")
    
    # Check if there are any other relationship indicators
    for key in parsed_data.keys():
        if 'link' in key.lower() or 'factor' in key.lower():
            print(f"\nFound potential relationship data: {key}")
            data = parsed_data[key]
            if data:
                print(f"Count: {len(data)}")
                if hasattr(data[0], 'data'):
                    print(f"Sample keys: {list(data[0].data.get('children', {}).keys())}")
    
    # Look at conceptual models and results chains for diagram relationships
    conceptual_models = parsed_data.get('conceptual_models', [])
    if conceptual_models:
        first_model = conceptual_models[0]
        print(f"\nFirst conceptual model ID: {first_model.element_id}")
        print(f"Model data keys: {list(first_model.data.get('children', {}).keys())}")
        
        children = first_model.data.get('children', {})
        for key, value in children.items():
            if 'factor' in key.lower() or 'link' in key.lower():
                print(f"\nFound diagram-related field: {key}")
                print(f"Value: {value}")


if __name__ == "__main__":
    inspect_relationships()
